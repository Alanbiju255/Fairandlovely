import os
import sys

def get_base_path():
    """Returns the base path for data storage.
    If running as an EXE, uses %APPDATA%/MakeupGST.
    Otherwise, uses the script directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as a bundled EXE
        appdata = os.environ.get("APPDATA")
        base = os.path.join(appdata, "MakeupGST")
    else:
        # Running as a script
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    os.makedirs(base, exist_ok=True)
    return base

BASE_DIR = get_base_path()
DATA_FOLDER = os.path.join(BASE_DIR, "data")
INVOICE_FOLDER = os.path.join(BASE_DIR, "invoices")

# Ensure folders exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(INVOICE_FOLDER, exist_ok=True)

# File paths
PRODUCTS_FILE = os.path.join(DATA_FOLDER, "products.csv")
SALES_FILE = os.path.join(DATA_FOLDER, "sales.csv")
EXPENSES_FILE = os.path.join(DATA_FOLDER, "expenses.csv")
