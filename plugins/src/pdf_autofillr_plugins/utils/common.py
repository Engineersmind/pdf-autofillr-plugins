"""
pdf_autofillr_plugins.utils.common

Shared utility functions — safe JSON handling, hashing, string helpers,
file utilities, retry with backoff, and a timing context manager.

These are pure-Python helpers with no external dependencies.
They were originally in plugins/core/common_utils.py in the sdk-exp repo
and are bundled here so plugin authors have them available without
importing from another package.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ── ID generation ─────────────────────────────────────────────────────────────

def generate_session_id() -> str:
    """Generate a unique session ID (UUID4 string)."""
    return str(uuid.uuid4())


# ── Hashing ───────────────────────────────────────────────────────────────────

def generate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """
    Generate a hex digest hash of a file.

    Args:
        file_path: Path to the file.
        algorithm: Any algorithm supported by hashlib (md5, sha1, sha256, …).

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algorithm)
    with open(file_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_content_hash(content: bytes, algorithm: str = "sha256") -> str:
    """
    Generate a hex digest hash of raw bytes.

    Args:
        content: Bytes to hash.
        algorithm: Hash algorithm.

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algorithm)
    h.update(content)
    return h.hexdigest()


# ── JSON helpers ──────────────────────────────────────────────────────────────

def safe_json_dumps(obj: Any, indent: Optional[int] = None) -> str:
    """
    Serialize *obj* to JSON, gracefully handling non-serialisable types.

    datetime → ISO string, objects with __dict__ → their dict, everything
    else → str().
    """
    def _default(o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "__dict__"):
            return o.__dict__
        return str(o)

    return json.dumps(obj, default=_default, indent=indent)


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Parse a JSON string, returning *default* on failure instead of raising.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse JSON: %s", exc)
        return default


# ── Dict helpers ──────────────────────────────────────────────────────────────

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dicts left-to-right (later dicts override earlier ones).
    None values in *dicts* are silently skipped.
    """
    result: Dict[str, Any] = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


# ── String helpers ────────────────────────────────────────────────────────────

def sanitize_filename(filename: str) -> str:
    """
    Remove or replace characters that are unsafe on most file systems.
    Also strips leading/trailing spaces and dots, and caps length at 255.
    """
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename.strip(". ")
    if len(filename) > 255:
        if "." in filename:
            name, ext = filename.rsplit(".", 1)
            filename = name[: 255 - len(ext) - 1] + "." + ext
        else:
            filename = filename[:255]
    return filename


def get_file_extension(filename: str) -> str:
    """Return the file extension including the dot, e.g. '.pdf'. Empty string if none."""
    return os.path.splitext(filename)[1]


def format_bytes(size: int) -> str:
    """Format a byte count as a human-readable string (e.g. '1.5 MB')."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate *s* to *max_length* characters, appending *suffix* if cut."""
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


# ── List helpers ──────────────────────────────────────────────────────────────

def chunk_list(lst: list, chunk_size: int) -> List[list]:
    """Split *lst* into sub-lists of at most *chunk_size* items each."""
    return [lst[i: i + chunk_size] for i in range(0, len(lst), chunk_size)]


# ── Retry ─────────────────────────────────────────────────────────────────────

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,),
) -> Any:
    """
    Call *func* up to *max_retries* + 1 times with exponential backoff.

    Args:
        func: Zero-argument callable to call.
        max_retries: Maximum number of retries after the first attempt.
        initial_delay: Seconds to wait before the first retry.
        backoff_factor: Multiplier applied to the delay after each retry.
        exceptions: Exception types that trigger a retry.

    Returns:
        The return value of *func* on success.

    Raises:
        The last caught exception if all attempts fail.
    """
    delay = initial_delay
    last_exc: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as exc:
            last_exc = exc
            if attempt < max_retries:
                logger.warning(
                    "Attempt %d/%d failed: %s. Retrying in %.1fs…",
                    attempt + 1, max_retries + 1, exc, delay,
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error("All %d attempts failed.", max_retries + 1)

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("retry_with_backoff: all attempts failed with no exception captured")


# ── Timer ─────────────────────────────────────────────────────────────────────

class Timer:
    """Context manager that measures wall-clock time for a named operation."""

    def __init__(self, name: str = "Operation") -> None:
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self) -> "Timer":
        self.start_time = time.time()
        return self

    def __exit__(self, *_: Any) -> None:
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time  # type: ignore[operator]
        logger.info("%s took %.2fs", self.name, self.duration)

    def get_duration_ms(self) -> float:
        """Duration in milliseconds (0.0 if not yet finished)."""
        return self.duration * 1000 if self.duration is not None else 0.0
