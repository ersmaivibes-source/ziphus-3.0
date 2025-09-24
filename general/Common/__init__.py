"""
general Common Module - Basic Utilities Consolidation
===================================================

Consolidates all common utilities and helper functions from across the codebase.
"""

from .utilities import CommonUtils
from .helpers import (
    generate_unique_id, generate_short_id, format_file_size, extract_urls_from_text,
    truncate_text, parse_duration, format_datetime, calculate_age, extract_chat_id_from_text,
    clean_html, escape_markdown, calculate_percentage, chunk_list, merge_dicts, safe_int,
    safe_float, time_ago, create_progress_bar, extract_domain_from_url, rate_limit_key,
    create_file_hash, get_file_extension, is_image_file, is_video_file, is_audio_file,
    is_document_file, get_mime_type, create_backup_filename, normalize_text, parse_command_args,
    is_weekend, get_season, create_temp_filename, Timer
)


class HelperFunctions:
    """Compatibility class for helper functions."""
    
    generate_unique_id = staticmethod(generate_unique_id)
    generate_short_id = staticmethod(generate_short_id)
    format_file_size = staticmethod(format_file_size)
    extract_urls_from_text = staticmethod(extract_urls_from_text)
    truncate_text = staticmethod(truncate_text)
    parse_duration = staticmethod(parse_duration)
    format_datetime = staticmethod(format_datetime)
    calculate_age = staticmethod(calculate_age)
    extract_chat_id_from_text = staticmethod(extract_chat_id_from_text)
    clean_html = staticmethod(clean_html)
    escape_markdown = staticmethod(escape_markdown)
    calculate_percentage = staticmethod(calculate_percentage)
    chunk_list = staticmethod(chunk_list)
    merge_dicts = staticmethod(merge_dicts)
    safe_int = staticmethod(safe_int)
    safe_float = staticmethod(safe_float)
    time_ago = staticmethod(time_ago)
    create_progress_bar = staticmethod(create_progress_bar)
    extract_domain_from_url = staticmethod(extract_domain_from_url)
    rate_limit_key = staticmethod(rate_limit_key)
    create_file_hash = staticmethod(create_file_hash)
    get_file_extension = staticmethod(get_file_extension)
    is_image_file = staticmethod(is_image_file)
    is_video_file = staticmethod(is_video_file)
    is_audio_file = staticmethod(is_audio_file)
    is_document_file = staticmethod(is_document_file)
    get_mime_type = staticmethod(get_mime_type)
    create_backup_filename = staticmethod(create_backup_filename)
    normalize_text = staticmethod(normalize_text)
    parse_command_args = staticmethod(parse_command_args)
    is_weekend = staticmethod(is_weekend)
    get_season = staticmethod(get_season)
    create_temp_filename = staticmethod(create_temp_filename)
    Timer = Timer


__all__ = ['CommonUtils', 'HelperFunctions']