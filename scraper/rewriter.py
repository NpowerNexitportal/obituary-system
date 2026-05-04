from deep_translator import GoogleTranslator
import re

def translate_text(text, source_lang, target_lang):
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        # Translator has a 5000 char limit per chunk.
        if len(text) > 4999:
            text = text[:4999]
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def rewrite_obituary(obituary_data):
    """
    Spins the obituary content using Google Translate:
    English -> Spanish -> French -> English
    Also appends (2026) to the exact source title.
    """
    raw_content = obituary_data.get('raw_content', '')
    title = obituary_data.get('title', 'Unknown Obituary')
    
    print(f"Spinning content for: {title}")
    
    # 1. Spin the content (EN -> ES -> FR -> EN)
    es_text = translate_text(raw_content, 'en', 'es')
    fr_text = translate_text(es_text, 'es', 'fr')
    final_en_text = translate_text(fr_text, 'fr', 'en')
    
    # Fallback to original if translation fails
    if not final_en_text or len(final_en_text) < 50:
        final_en_text = raw_content
        
    # 2. Append (2026) to the title
    final_title = f"{title.strip()} (2026)"
    
    # 3. Meta description (first 150 chars)
    meta_description = final_en_text[:150] + "..." if len(final_en_text) > 150 else final_en_text
    
    # Generate slug from title
    slug = re.sub(r'[^a-z0-9]+', '-', final_title.lower()).strip('-')

    return {
        "name": final_title,  # Used loosely
        "title": final_title,
        "slug": slug,
        "content": final_en_text,
        "meta_description": meta_description,
        "location": "Unknown",
        "date_of_death": "Recently",
        "source_url": obituary_data.get('source_url', '') # Tracking internally, not displayed
    }
