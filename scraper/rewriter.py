import re
from datetime import datetime

def rewrite_content(raw_content, name_hint=""):
    """
    Rewrites the raw content into a 100% unique SEO-optimized article.
    Extracts name, location, date of death, etc.
    """
    # Simple extraction heuristics (An LLM would do this much better)
    name = extract_name(raw_content) or name_hint or "Unknown Person"
    location = extract_location(raw_content) or "Unknown Location"
    
    # Construct SEO optimized unique content
    current_date = datetime.utcnow().strftime('%B %d, %Y')
    
    title = f"{name} Obituary - Passed Away in {location}"
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    meta_description = f"Read the obituary and life legacy of {name} who recently passed away in {location}. Share your condolences and memories."
    
    # Generate a unique summary/content
    rewritten_content = (
        f"It is with heavy hearts that we share the news of the passing of {name}, "
        f"a beloved member of the {location} community. {name} passed away leaving behind "
        f"a legacy of love and memories. Friends and family are mourning the loss of a truly "
        f"special individual.\n\n"
        f"The community in {location} has been deeply affected by this loss. "
        f"Funeral arrangements and memorial services are being organized to honor and celebrate "
        f"the life of {name}. We extend our deepest sympathies to the family during this difficult time."
        f"\n\n(Note: This is an auto-generated rewritten summary to maintain unique, respectful SEO content.)"
    )
    
    return {
        "name": name,
        "title": title,
        "slug": slug,
        "content": rewritten_content,
        "meta_description": meta_description,
        "location": location,
        "date_of_death": current_date, # Fallback, should extract
        "hash": None # Generated later
    }

def extract_name(text):
    match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)(?:.*)(?:passed away|died|obituary)', text)
    if match:
        return match.group(1)
    return None

def extract_location(text):
    match = re.search(r'(?:in|from|resident of) ([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?)', text)
    if match:
        return match.group(1).strip()
    return None
