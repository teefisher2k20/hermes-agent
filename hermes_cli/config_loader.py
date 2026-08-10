"""
Unified Configuration Singleton for Hermes Agent.

Provides thread-safe, profile-aware loading of config.yaml and .env settings
across CLI, Gateway, and API endpoints.
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, Optional

from hermes_cli.config import DEFAULT_CONFIG, load_config as _base_load_config, save_config as _base_save_config

logger = logging.getLogger(__name__)

_config_lock = threading.Lock()
_cached_config: Optional[Dict[str, Any]] = None


class HermesConfigProvider:
    """Thread-safe configuration manager singleton."""

    @classmethod
    def get_config(cls, reload: bool = False) -> Dict[str, Any]:
        """Return the active merged configuration dictionary."""
        global _cached_config
        with _config_lock:
            if _cached_config is None or reload:
                _cached_config = _base_load_config()
            return dict(_cached_config)

    @classmethod
    def set_value(cls, dotpath: str, value: Any) -> None:
        """Set a configuration setting by dotpath and persist to disk."""
        global _cached_config
        with _config_lock:
            config = cls.get_config(reload=True)
            parts = dotpath.split(".")
            curr = config
            for p in parts[:-1]:
                if p not in curr or not isinstance(curr[p], dict):
                    curr[p] = {}
                curr = curr[p]
            curr[parts[-1]] = value
            _base_save_config(config)
            _cached_config = config


def get_config(reload: bool = False) -> Dict[str, Any]:
    """Public helper to get unified config."""
    return HermesConfigProvider.get_config(reload=reload)


def set_config_value(dotpath: str, value: Any) -> None:
    """Public helper to set unified config value."""
    HermesConfigProvider.set_value(dotpath, value)
