import re

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_mentions(text, brand_profile):
    text_norm = normalize(text)

    mentioned_brands = []
    mentioned_domains = []

    # User brand
    if normalize(brand_profile.brand_name) in text_norm:
        mentioned_brands.append(brand_profile.brand_name)

    if brand_profile.domain_name and normalize(brand_profile.domain_name) in text_norm:
        mentioned_domains.append(brand_profile.domain_name)

    # Competitors
    for comp in brand_profile.competitors.all():
        if normalize(comp.brand_name) in text_norm:
            mentioned_brands.append(comp.brand_name)

        if normalize(comp.domain_name) in text_norm:
            mentioned_domains.append(comp.domain_name)

    return mentioned_brands, mentioned_domains
