"""
pdf_autofillr_plugins.utils

Shared utility helpers for plugin authors.

    from pdf_autofillr_plugins.utils import (
        generate_session_id,
        generate_file_hash,
        safe_json_dumps,
        safe_json_loads,
        merge_dicts,
        sanitize_filename,
        format_bytes,
        truncate_string,
        chunk_list,
        retry_with_backoff,
        Timer,
    )
"""

from pdf_autofillr_plugins.utils.common import (
    Timer,
    chunk_list,
    format_bytes,
    generate_content_hash,
    generate_file_hash,
    generate_session_id,
    get_file_extension,
    merge_dicts,
    retry_with_backoff,
    safe_json_dumps,
    safe_json_loads,
    sanitize_filename,
    truncate_string,
)

__all__ = [
    "Timer",
    "chunk_list",
    "format_bytes",
    "generate_content_hash",
    "generate_file_hash",
    "generate_session_id",
    "get_file_extension",
    "merge_dicts",
    "retry_with_backoff",
    "safe_json_dumps",
    "safe_json_loads",
    "sanitize_filename",
    "truncate_string",
]
