"""
general Language Module - General and general Language Texts.

This module contains all general/general language texts that are not specific to any domain.
It includes navigation, welcome messages, general errors, and basic bot functionality texts.
"""

from .core_translations_en import CORE_EN_TEXTS
from .core_translations_fa import CORE_FA_TEXTS

__all__ = [
    'CORE_EN_TEXTS',
    'CORE_FA_TEXTS',
    'get_core_text'
]

def get_core_text(key: str, lang_code: str = 'en') -> str:
    """
    Get general language text by key and language code.
    
    Args:
        key: Text key
        lang_code: Language code ('en' or 'fa')
        
    Returns:
        Translated text or key if not found
    """
    texts = CORE_FA_TEXTS if lang_code == 'fa' else CORE_EN_TEXTS
    return texts.get(key, key)