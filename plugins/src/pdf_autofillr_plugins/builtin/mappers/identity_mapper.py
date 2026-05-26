"""
Built-in: IdentityMapperPlugin

Maps fields by matching extracted field names directly to schema keys (exact match,
then snake_case normalisation). Useful as a baseline mapper and for testing.
Registered under category="mapper", name="identity-mapper".
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from pdf_autofillr_plugins.decorators import plugin
from pdf_autofillr_plugins.interfaces import MapperPlugin, PluginMetadata


def _to_snake(name: str) -> str:
    """Normalise a field name to snake_case for loose matching."""
    s = re.sub(r"[\s\-]+", "_", name.strip().lower())
    return re.sub(r"[^a-z0-9_]", "", s)


@plugin(
    category="mapper",
    name="identity-mapper",
    version="1.0.0",
    author="PDF AutoFillr Team",
    description="Maps fields by exact name or snake_case normalisation. Baseline mapper.",
    tags=["identity", "baseline", "builtin"],
    priority=1,
)
class IdentityMapperPlugin(MapperPlugin):
    """
    Identity / baseline mapper.

    Strategy (in order):
    1. Exact match between extracted field name and schema key.
    2. Snake-case normalised match.
    3. Field is left unmapped.
    """

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="identity-mapper",
            version="1.0.0",
            author="PDF AutoFillr Team",
            description="Maps fields by exact name or snake_case normalisation",
            category="mapper",
            tags=["identity", "baseline", "builtin"],
        )

    def supports_schema(self, schema: Dict[str, Any]) -> bool:
        return True  # accepts any schema

    def map_fields(
        self,
        extracted_fields: List[Dict[str, Any]],
        target_schema: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        schema_keys = set(target_schema.keys()) if target_schema else set()
        snake_index: Dict[str, str] = {_to_snake(k): k for k in schema_keys}

        mapped: Dict[str, Any] = {}
        unmapped: List[str] = []
        mapping_info: List[Dict[str, Any]] = []

        for field in extracted_fields:
            name = field.get("name", "")
            value = field.get("value", "")
            confidence = field.get("confidence", 1.0)

            # 1. Exact match
            if name in schema_keys:
                mapped[name] = value
                mapping_info.append(
                    {
                        "source": name,
                        "target": name,
                        "method": "exact",
                        "confidence": confidence,
                    }
                )
                continue

            # 2. Snake-case match
            snake = _to_snake(name)
            if snake in snake_index:
                target = snake_index[snake]
                mapped[target] = value
                mapping_info.append(
                    {
                        "source": name,
                        "target": target,
                        "method": "snake_case",
                        "confidence": confidence * 0.9,
                    }
                )
                continue

            # 3. No schema — pass through as-is
            if not schema_keys:
                mapped[name] = value
                mapping_info.append(
                    {
                        "source": name,
                        "target": name,
                        "method": "passthrough",
                        "confidence": confidence,
                    }
                )
                continue

            unmapped.append(name)

        total = len(extracted_fields)
        return {
            "mapped_fields": mapped,
            "unmapped_fields": unmapped,
            "mapping_info": mapping_info,
            "mapper": "identity-mapper",
            "confidence": (sum(i["confidence"] for i in mapping_info) / total if total else 0.0),
            "coverage": len(mapped) / total if total else 0.0,
        }

    def get_mapping_confidence(
        self,
        extracted_fields: List[Dict[str, Any]],
        target_schema: Dict[str, Any],
    ) -> float:
        result = self.map_fields(extracted_fields, target_schema)
        return float(result.get("confidence", 0.0))
