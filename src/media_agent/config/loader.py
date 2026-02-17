"""Product configuration loader."""

import json
from pathlib import Path
from typing import Optional

from ..config import get_config_dir


def load_product_config(product_name: str) -> Optional[dict]:
    """Load product configuration from JSON file."""
    config_dir = get_config_dir() / "products"
    
    # Try different extensions
    for ext in [".json", ".yaml", ".yml"]:
        config_path = config_dir / f"{product_name.lower()}{ext}"
        if config_path.exists():
            with open(config_path, "r") as f:
                if ext == ".json":
                    return json.load(f)
                # Add yaml support if needed
    
    return None


def list_available_products() -> list[str]:
    """List all available product configs."""
    config_dir = get_config_dir() / "products"
    if not config_dir.exists():
        return []
    
    products = []
    for f in config_dir.iterdir():
        if f.suffix in [".json", ".yaml", ".yml"]:
            products.append(f.stem)
    return products


def get_faqs_from_config(product_name: str) -> list[dict]:
    """Extract FAQs from product config."""
    config = load_product_config(product_name)
    if config and "faq" in config:
        return config["faq"]
    return []
