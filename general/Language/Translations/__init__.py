"""Language translations compatibility layer for Ziphus Bot."""

# Import all text dictionaries from the distributed language files
from general.Language.core_translations_en import CORE_EN_TEXTS
from general.Language.core_translations_fa import CORE_FA_TEXTS
from Admin.Language.admin_translations_en import ADMIN_TRANSLATIONS_EN
from Admin.Language.admin_translations_fa import ADMIN_TRANSLATIONS_FA
from Users.Language.user_translations_en import USER_TRANSLATIONS_EN
from Users.Language.user_translations_fa import USER_TRANSLATIONS_FA

# Combine all texts into a single dictionary for each language
EN_TEXTS = {}
EN_TEXTS.update(CORE_EN_TEXTS)
EN_TEXTS.update(ADMIN_TRANSLATIONS_EN)
EN_TEXTS.update(USER_TRANSLATIONS_EN)

FA_TEXTS = {}
FA_TEXTS.update(CORE_FA_TEXTS)
FA_TEXTS.update(ADMIN_TRANSLATIONS_FA)
FA_TEXTS.update(USER_TRANSLATIONS_FA)

def get_text_sync(key: str, lang: str = 'en', **kwargs) -> str:
    """
    Get translated text synchronously with optional formatting.
    
    Args:
        key: Translation key
        lang: Language code ('en' or 'fa')
        **kwargs: Formatting parameters
        
    Returns:
        Translated and formatted text
    """
    # Select the appropriate language dictionary
    texts = FA_TEXTS if lang == 'fa' else EN_TEXTS
    
    # Get the translation or return key if not found
    text = texts.get(key, key)
    
    # Format with provided kwargs if any
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted text
            pass
            
    return text

async def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """
    Get translated text asynchronously with optional formatting.
    
    Args:
        key: Translation key
        lang: Language code ('en' or 'fa')
        **kwargs: Formatting parameters
        
    Returns:
        Translated and formatted text
    """
    # For this simple implementation, just call the sync version
    # In a more complex system, this could handle async operations
    return get_text_sync(key, lang, **kwargs)

__all__ = ['get_text_sync', 'get_text', 'EN_TEXTS', 'FA_TEXTS']