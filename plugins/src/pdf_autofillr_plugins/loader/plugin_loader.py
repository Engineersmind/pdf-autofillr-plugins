"""
Plugin Loader

Loads community-submitted plugin manifests from the registry/ folder,
validates them against plugin.schema.json, and registers the plugins
into the existing PluginRegistry / PluginManager.

Usage::

    from pdf_autofillr_plugins.loader import PluginLoader

    loader = PluginLoader()
    loader.load_all()          # loads all manifests from registry/
    loader.load("my-plugin")   # loads a single manifest by name
"""

from __future__ import annotations

import importlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default paths
_PACKAGE_ROOT = Path(__file__).parent.parent
_REGISTRY_DIR = _PACKAGE_ROOT / "registry"
_SCHEMA_PATH  = _PACKAGE_ROOT / "plugin.schema.json"


class PluginLoader:
    """
    Runtime loader for community plugin manifests.

    Reads JSON manifests from the registry/ folder, optionally validates
    them against plugin.schema.json, then imports and registers the
    plugin class into a PluginRegistry instance.

    Args:
        registry_dir: Path to the registry/ folder (defaults to the
                      built-in registry/ inside the package).
        schema_path:  Path to plugin.schema.json for manifest validation.
                      Pass None to skip validation.
    """

    def __init__(
        self,
        registry_dir: Optional[Path] = None,
        schema_path: Optional[Path] = _SCHEMA_PATH,
    ) -> None:
        self.registry_dir = Path(registry_dir) if registry_dir else _REGISTRY_DIR
        self.schema_path  = Path(schema_path) if schema_path else None
        self._schema: Optional[Dict[str, Any]] = None
        self._loaded: List[str] = []

    # ── Schema ────────────────────────────────────────────────────────────────

    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """Load plugin.schema.json once and cache it."""
        if self._schema is not None:
            return self._schema
        if self.schema_path and self.schema_path.exists():
            try:
                self._schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
                return self._schema
            except Exception as e:
                logger.warning("Could not load schema from %s: %s", self.schema_path, e)
        return None

    def _validate_manifest(self, manifest: Dict[str, Any], name: str) -> bool:
        """
        Validate a manifest dict against plugin.schema.json.

        Uses jsonschema if available; skips silently if not installed.

        Returns:
            True if valid (or schema not available), False if invalid.
        """
        schema = self._load_schema()
        if not schema:
            return True  # no schema — skip validation

        try:
            import jsonschema
            jsonschema.validate(instance=manifest, schema=schema)
            return True
        except ImportError:
            logger.debug("jsonschema not installed — skipping manifest validation")
            return True
        except Exception as e:
            logger.error("Manifest '%s' failed schema validation: %s", name, e)
            return False

    # ── Loading ───────────────────────────────────────────────────────────────

    def load_all(self) -> List[str]:
        """
        Load all JSON manifests found in the registry/ folder.

        Returns:
            List of successfully loaded plugin names.
        """
        if not self.registry_dir.exists():
            logger.warning("Registry directory not found: %s", self.registry_dir)
            return []

        loaded = []
        for manifest_file in sorted(self.registry_dir.glob("*.json")):
            name = manifest_file.stem
            if self._load_manifest_file(manifest_file):
                loaded.append(name)

        logger.info("PluginLoader: loaded %d plugin(s) from %s", len(loaded), self.registry_dir)
        return loaded

    def load(self, plugin_name: str) -> bool:
        """
        Load a single plugin manifest by name.

        Args:
            plugin_name: Filename stem of the manifest (without .json).

        Returns:
            True if loaded successfully.
        """
        manifest_file = self.registry_dir / f"{plugin_name}.json"
        if not manifest_file.exists():
            logger.error("Manifest not found: %s", manifest_file)
            return False
        return self._load_manifest_file(manifest_file)

    def _load_manifest_file(self, manifest_file: Path) -> bool:
        """Parse, validate, and import a single manifest file."""
        name = manifest_file.stem
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error("Failed to parse manifest '%s': %s", name, e)
            return False

        if not self._validate_manifest(manifest, name):
            return False

        return self._import_plugin(manifest, name)

    def _import_plugin(self, manifest: Dict[str, Any], name: str) -> bool:
        """
        Import the plugin class declared in a manifest and register it.

        Manifest must contain:
            module   (str): dotted module path, e.g. "my_package.my_plugin"
            class    (str): class name, e.g. "MyPlugin"
            category (str): plugin category, e.g. "extractor"

        Returns:
            True if imported and registered successfully.
        """
        module_path = manifest.get("module")
        class_name  = manifest.get("class")
        category    = manifest.get("category")

        if not all([module_path, class_name, category]):
            logger.error(
                "Manifest '%s' missing required fields (module, class, category)", name
            )
            return False

        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            logger.info(
                "PluginLoader: registered '%s' (%s) from %s",
                name, category, module_path,
            )
            self._loaded.append(name)
            return True

        except ImportError as e:
            logger.error("Cannot import module '%s' for plugin '%s': %s", module_path, name, e)
        except AttributeError:
            logger.error("Class '%s' not found in module '%s'", class_name, module_path)
        except Exception as e:
            logger.error("Unexpected error loading plugin '%s': %s", name, e)

        return False

    # ── Introspection ─────────────────────────────────────────────────────────

    def list_manifests(self) -> List[str]:
        """Return names of all JSON manifests present in registry/."""
        if not self.registry_dir.exists():
            return []
        return [f.stem for f in sorted(self.registry_dir.glob("*.json"))]

    def list_loaded(self) -> List[str]:
        """Return names of plugins successfully loaded this session."""
        return list(self._loaded)