#!/usr/bin/env python3
"""Shared seed-to-category classifier used to build hub page link indexes.

Ground truth comes from the SEEDS/SEEDS_BY_CAT dicts already baked into
gen_200_pages.py and gen_seasonal_pages.py (the actual category the site's
own generators assigned). Anything not covered by those dicts falls back
to keyword matching against a per-category vocabulary.
"""
from __future__ import annotations

import re

CATEGORY_HUBS = {
    "electronics": "/electronics-deals.html",
    "home": "/home-deals.html",
    "kitchen": "/kitchen-deals.html",
    "tools": "/tools-deals.html",
    "kids": "/kids-deals.html",
    "beauty": "/beauty-deals.html",
    "fitness": "/fitness-deals.html",
    "pets": "/pets-deals.html",
}

# Ground truth from scripts/gen_200_pages.py SEEDS + scripts/gen_seasonal_pages.py SEEDS_BY_CAT
GROUND_TRUTH = {
    "electronics": [
        "usb c charger", "usb c cable", "wireless charger", "power bank",
        "bluetooth speaker", "noise cancelling headphones", "gaming headset",
        "webcam", "wifi router", "surge protector", "smart plug",
        "smart light bulbs", "hdmi cable", "screen protector",
        "phone car mount", "dash cam",
    ],
    "home": [
        "bed sheets", "mattress topper", "blackout curtains", "storage bins",
        "shoe rack", "desk lamp", "humidifier", "space heater",
        "air purifier", "steam mop", "trash can", "shower curtain",
        "shower head", "doormat", "closet organizer",
    ],
    "kitchen": [
        "air fryer", "air fryer accessories", "rice cooker", "coffee maker",
        "electric kettle", "blender", "toaster oven", "food scale",
        "meal prep containers", "nonstick cookware", "bento lunch box",
        "immersion blender",
    ],
    "tools": [
        "cordless drill", "tool set", "toolbox", "socket set",
        "extension cord", "tape measure", "laser level", "flashlight",
        "work gloves", "cable management",
    ],
    "kids": [
        "kids headphones", "kids backpack", "science kits",
        "science kits for kids", "learning toys", "building block sets",
        "board games", "kids water bottle", "toddler balance bike",
    ],
    "beauty": [
        "vitamin c serum", "retinol serum", "niacinamide serum", "sunscreen",
        "makeup brush set", "blow dryer", "flat iron", "electric toothbrush",
        "skincare fridge",
    ],
    "fitness": [
        "adjustable dumbbells", "resistance bands", "yoga mat", "foam roller",
        "ab roller", "pull up bar", "kettlebell", "massage gun",
        "fitness tracker",
    ],
    "pets": [
        "dog bed", "cat tree", "cat litter box", "pet water fountain",
        "pet grooming brush", "dog grooming kit", "interactive cat toy",
        "pet car seat cover",
    ],
}

SEED_TO_CATEGORY: dict[str, str] = {}
for _cat, _seeds in GROUND_TRUTH.items():
    for _s in _seeds:
        SEED_TO_CATEGORY[_s] = _cat

# Keyword fallback for the hundreds of seeds not covered by the ground
# truth above. Order matters -- first matching category wins, so more
# specific keywords are listed before generic ones.
KEYWORD_RULES = [
    ("kitchen", [
        "air fryer", "kitchen", "cookware", "skillet", "pan", "pot", "knife",
        "cutting board", "blender", "kettle", "toaster", "coffee", "rice cooker",
        "food scale", "meal prep", "bento", "lunch box", "spice", "baking",
        "oven", "grill", "griddle", "mixer", "food processor", "dish", "mug",
        "water bottle", "thermometer", "can opener", "utensil", "storage container",
        "pressure cooker", "slow cooker", "colander", "ice maker", "milk frother",
        "mixing bowl", "salad spinner", "waffle maker", "water filter pitcher",
        "measuring cup",
    ]),
    ("electronics", [
        "usb", "charger", "cable", "speaker", "headphone", "headset", "earbud",
        "webcam", "router", "wifi", "smart plug", "light bulb", "hdmi",
        "screen protector", "phone mount", "dash cam", "power bank", "ssd",
        "hard drive", "monitor", "keyboard", "mouse", "laptop stand", "tablet stand",
        "projector", "smart watch", "smartwatch", "drone", "gaming", "console",
        "tripod", "microphone", "ring light", "adapter", "hub", "dock",
        "bluetooth tracker", "bluetooth transmitter", "ethernet", "graphics tablet",
        "laptop cooling", "laptop sleeve", "led strip", "micro sd", "sd card",
        "security camera", "smart lock", "smart power strip", "smart thermostat",
        "smoke detector", "carbon monoxide detector", "streaming stick",
        "video doorbell", "water leak detector", "wireless presenter",
        "phone gimbal", "electronics",
    ]),
    ("tools", [
        "drill", "tool", "wrench", "socket", "screwdriver", "ladder", "saw",
        "level", "flashlight", "work glove", "extension cord", "tape measure",
        "hammer", "pliers", "generator", "air compressor", "sander", "impact driver",
    ]),
    ("kids", [
        "kids", "toddler", "baby", "toy", "science kit", "learning", "building block",
        "board game", "backpack", "stroller", "crib", "night light", "art easel",
        "smartwatch for kid", "magnetic tile", "indoor climbing set", "car seat accessories",
    ]),
    ("beauty", [
        "serum", "sunscreen", "makeup", "hair dryer", "blow dryer", "flat iron",
        "curling iron", "toothbrush", "skincare", "beauty", "nail", "lash",
        "razor", "shaver", "perfume", "moisturizer",
    ]),
    ("fitness", [
        "dumbbell", "resistance band", "yoga", "foam roller", "ab roller",
        "pull up bar", "kettlebell", "massage gun", "fitness tracker", "gym",
        "exercise", "treadmill", "bike trainer", "jump rope", "weight bench",
    ]),
    ("pets", [
        "dog", "cat", "pet ", "pet-", "litter", "leash", "collar", "aquarium",
        "fish tank", "bird cage",
    ]),
    ("home", [
        "bed sheet", "bed frame", "mattress", "curtain", "storage bin", "shoe rack",
        "desk lamp", "humidifier", "space heater", "air purifier", "steam mop",
        "trash can", "shower", "doormat", "closet", "rug", "pillow", "blanket",
        "vacuum", "candle", "furniture", "organizer", "lamp", "mirror", "wall art",
        "planter", "garden", "bath mat", "bath towel", "bathroom storage",
        "entryway bench", "floating shelves", "garage shelving", "ironing board",
        "laundry", "nightstand", "standing desk converter", "storage ottoman",
        "tower fan", "microfiber cloth", "home",
    ]),
]


def classify(seed_phrase: str) -> str:
    """Return the best-guess category slug for a human-readable seed phrase."""
    if seed_phrase in SEED_TO_CATEGORY:
        return SEED_TO_CATEGORY[seed_phrase]
    lower = f" {seed_phrase.lower()} "
    for cat, keywords in KEYWORD_RULES:
        for kw in keywords:
            if kw in lower:
                return cat
    return "home"  # broad catch-all; "home" hub covers general household goods
