import pandas as pd

from modules.paths import SALES_FILE, EXPENSES_FILE

def generate_profit_loss():
    sales = pd.read_csv(SALES_FILE)
    expenses = pd.read_csv(EXPENSES_FILE)

    total_sales = sales["total"].sum()
    total_expenses = expenses["amount"].sum()

    profit = total_sales - total_expenses

    return total_sales, total_expenses, profit
def generate_balance_sheet():
    sales = pd.read_csv(SALES_FILE)
    expenses = pd.read_csv(EXPENSES_FILE)

    assets = sales["total"].sum()
    liabilities = expenses["amount"].sum()
    equity = assets - liabilities

    return assets, liabilities, equity
def sales_by_salesperson():
    sales = pd.read_csv("data/sales.csv")
    return sales.groupby("salesperson")["total"].sum()
