import re
from typing import Optional, List
from .models import RequirementOutput

WORD_TO_NUM = {
    "one": 1, "a": 1, "an": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

STYLE_MAPPINGS = [
    (r'modern\s*kerala(?:\s*style)?', 'modern_kerala'),
    (r'traditional\s*kerala(?:\s*style)?', 'traditional_kerala'),
    (r'contemporary(?:\s*style)?', 'contemporary'),
    (r'modern(?:\s*style)?', 'modern'),
    (r'luxury(?:\s*house)?(?:\s*style)?', 'luxury'),
]

TYPE_KEYWORDS = ["villa", "bungalow", "duplex", "house"]

SPECIAL_REQS = [
    "master bedroom with attached bathroom",
    "large kitchen",
    "covered parking",
    "front balcony",
    "family living",
    "home office",
    "prayer room",
    "servant room",
    "utility room",
    "spacious living room"
]

def text_to_num(text: str) -> Optional[int]:
    if not text:
        return None
    t = text.lower().strip()
    if t.isdigit():
        return int(t)
    return WORD_TO_NUM.get(t)

def parse_requirements(text: str) -> RequirementOutput:
    req = RequirementOutput(source_text=text)
    t = text.lower()

    # Style
    for pattern, style in STYLE_MAPPINGS:
        if re.search(r'\b' + pattern + r'\b', t):
            req.house_style = style
            break

    # Type
    for h_type in TYPE_KEYWORDS:
        if re.search(r'\b' + h_type + r'\b', t):
            req.house_type = h_type
            if h_type == "duplex":
                req.floors = 2
            break

    # Bedrooms
    bed_match = re.search(r'(?<!no\s)(?<!without\s)\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:-?\s*bhk|bedroom|bed)s?\b', t)
    if bed_match:
        req.bedrooms = text_to_num(bed_match.group(1))

    # Floors
    floor_match = re.search(r'(?<!no\s)(?<!without\s)\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|single)\s*(?:-?\s*floor|-?\s*storey|-?\s*story)s?\b', t)
    if floor_match:
        val = floor_match.group(1)
        if val == "single":
            req.floors = 1
        else:
            req.floors = text_to_num(val)

    # Bathrooms
    bath_match = re.search(r'(?<!no\s)(?<!without\s)\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:-?\s*bathroom|-?\s*bath)s?\b', t)
    if bath_match:
        req.bathrooms = text_to_num(bath_match.group(1))

    # Parking
    if re.search(r'\b(?:no|without)\s*parking\b', t):
        req.parking_spaces = 0
    else:
        park_match1 = re.search(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:-?\s*car(?:s)? parking)\b', t)
        park_match2 = re.search(r'\bparking for\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+car(s)?\b', t)
        if park_match1:
            req.parking_spaces = text_to_num(park_match1.group(1))
        elif park_match2:
            req.parking_spaces = text_to_num(park_match2.group(1))

    # Balcony
    if re.search(r'\b(?:no|without)\s*balcon(?:y|ies)\b', t):
        req.balconies = 0
    else:
        balcony_match = re.search(r'\b(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:-?\s*balcon(?:y|ies))\b', t)
        if balcony_match:
            req.balconies = text_to_num(balcony_match.group(1))
        elif re.search(r'\bbalcon(?:y|ies)\b', t):
            req.balconies = 1

    # Terrace
    if re.search(r'\b(?:no|without)\s*(?:rooftop\s*)?terraces?\b', t):
        req.terraces = 0
    else:
        terrace_match = re.search(r'\b(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:rooftop\s*)?terraces?\b', t)
        if terrace_match:
            req.terraces = text_to_num(terrace_match.group(1))
        elif re.search(r'\b(?:rooftop\s*)?terrace\b', t):
            req.terraces = 1

    # Plot dimensions
    # 30x50, 30 x 50, 30 ft x 50 ft, plot 30 by 50 feet
    plot_match = re.search(r'(?:plot\s+)?(\d+(?:\.\d+)?)\s*(?:ft|feet)?\s*(?:x|by)\s*(\d+(?:\.\d+)?)\s*(?:ft|feet)?', t)
    if plot_match:
        req.plot_width = float(plot_match.group(1))
        req.plot_depth = float(plot_match.group(2))

    # Road side
    # road on north, north road, road side north
    road_dirs = ["north", "south", "east", "west"]
    for d in road_dirs:
        if re.search(rf'\b(?:road on {d}|{d} road|road side {d})\b', t):
            req.road_side = d
            break

    # Entrance direction
    for d in road_dirs:
        if re.search(rf'\b(?:{d}\s*entrance|entrance facing {d}|main entrance {d}|{d}\s*-?\s*facing entrance)\b', t):
            req.entrance_direction = d
            break

    # Roof type
    if re.search(r'\b(flat roof|terrace roof|modern flat roof)\b', t):
        req.roof_type = "flat"
    elif re.search(r'\b(pitched roof|gable roof|sloped roof)\b', t):
        req.roof_type = "pitched"
    elif req.house_style in ["modern", "modern_kerala", "contemporary"]:
        req.roof_type = "flat"

    # Special requirements
    specials = []
    text_for_specials = t
    for sr in sorted(SPECIAL_REQS, key=len, reverse=True):
        if sr in text_for_specials:
            specials.append(sr)
            text_for_specials = text_for_specials.replace(sr, "")
            
    if re.search(r'\b(garden|landscap(?:e|ing))\b', t):
        specials.append("landscaping")
        
    req.special_requirements = specials

    return req
