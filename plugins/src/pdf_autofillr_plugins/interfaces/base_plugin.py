"""
Base Plugin Interface

All plugins must inherit from BasePlugin and implement required methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PluginMetadata:
    """Plugin metadata"""

    name: str
    version: str
    author: str
    description: str
    category: str
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    config_schema: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class BasePlugin(ABC):
    """
    Base class for all plugins.

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with optional configuration.

        Args:
            config: Plugin-specific configuration dictionary
        """
        self.config = config or {}
        self._initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.

        Returns:
            PluginMetadata with plugin information
        """
        pass

    @property
    def name(self) -> str:
        """Plugin name"""
        return self.get_metadata().name

    @property
    def version(self) -> str:
        """Plugin version"""
        return self.get_metadata().version

    @property
    def category(self) -> str:
        """Plugin category"""
        return self.get_metadata().category

    @property
    def author(self) -> str:
        """Plugin author"""
        return self.get_metadata().author

    @property
    def description(self) -> str:
        """Plugin description"""
        return self.get_metadata().description

    def initialize(self) -> None:
        """
        Initialize plugin resources.

        Called once when plugin is loaded. Override to perform setup.
        """
        self._initialized = True

    def shutdown(self) -> None:
        """
        Clean up plugin resources.

        Called when plugin is unloaded. Override to perform cleanup.
        """
        self._initialized = False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        # Default: accept any config
        return True

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    @property
    def priority(self) -> int:
        """Plugin priority (higher = loaded first by find_extractor/find_mapper)"""
        return getattr(self.__class__, "_plugin_priority", 100)

    @property
    def tags(self) -> list:
        """Plugin tags"""
        return getattr(self.__class__, "_plugin_tags", [])

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized"""
        return self._initialized

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}')"

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
