from pathlib import Path
import pandas as pd

# Smart_AI folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Smart_AI/data folder
DATA_DIR = PROJECT_ROOT / "data"

def load_products():
    return pd.read_csv(DATA_DIR / "products.csv")


def load_reviews():
    return pd.read_csv(DATA_DIR / "reviews.csv")


def load_store_policies():
    return pd.read_csv(DATA_DIR / "store_policies.csv")