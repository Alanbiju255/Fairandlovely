import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import pandas as pd
import os
from datetime import datetime

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from modules.paths import PRODUCTS_FILE, SALES_FILE, EXPENSES_FILE, INVOICE_FOLDER

# ================== SAFE FILE CREATION ==================
if not os.path.exists(PRODUCTS_FILE) or os.path.getsize(PRODUCTS_FILE) == 0:
    pd.DataFrame(columns=["id","name","price","gst"]).to_csv(PRODUCTS_FILE, index=False)

if not os.path.exists(SALES_FILE) or os.path.getsize(SALES_FILE) == 0:
    pd.DataFrame(columns=["invoice_no","date","customer","service","price","gst","total"]).to_csv(SALES_FILE, index=False)

if not os.path.exists(EXPENSES_FILE) or os.path.getsize(EXPENSES_FILE) == 0:
    pd.DataFrame(columns=["date","description","amount"]).to_csv(EXPENSES_FILE, index=False)

# ================== APP WINDOW ==================
app = ttk.Window(themename="flatly")
app.title("Fairandlovely - Management System")
app.geometry("1300x800")

# Set window icon
if os.path.exists("logo.ico"):
    app.iconbitmap("logo.ico")

# ================== MAIN NOTEBOOK ==================
notebook = ttk.Notebook(app, bootstyle="primary")
notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

billing_frame = ttk.Frame(notebook)
reports_frame = ttk.Frame(notebook)
balance_sheet_frame = ttk.Frame(notebook)

notebook.add(billing_frame, text=" 📝 BILLING ")
notebook.add(reports_frame, text=" 📊 REPORTS & ANALYTICS ")
notebook.add(balance_sheet_frame, text=" 🏢 BALANCE SHEET ")

# ================== BILLING TAB LOGIC ==================

# --- ADD SERVICE SECTION ---
add_frame = ttk.LabelFrame(billing_frame, text="Add New Item to Menu")
add_frame.pack(fill=X, padx=20, pady=10)

name_entry = ttk.Entry(add_frame, width=25)
price_entry = ttk.Entry(add_frame, width=15)
gst_entry = ttk.Entry(add_frame, width=10)

ttk.Label(add_frame, text="Service Name").grid(row=0, column=0, padx=5)
name_entry.grid(row=0, column=1, padx=5, pady=5)
ttk.Label(add_frame, text="Base Price").grid(row=0, column=2, padx=5)
price_entry.grid(row=0, column=3, padx=5, pady=5)
ttk.Label(add_frame, text="GST %").grid(row=0, column=4, padx=5)
gst_entry.grid(row=0, column=5, padx=5, pady=5)

def add_item():
    if not name_entry.get(): return
    try:
        df = pd.read_csv(PRODUCTS_FILE)
        new_id = len(df) + 1
        df.loc[len(df)] = [new_id, name_entry.get(), float(price_entry.get()), float(gst_entry.get())]
        df.to_csv(PRODUCTS_FILE, index=False)
        load_products()
        name_entry.delete(0, END); price_entry.delete(0, END); gst_entry.delete(0, END)
    except Exception as e:
        messagebox.showerror("Error", f"Could not add item: {e}")

ttk.Button(add_frame, text="Add to Menu", bootstyle="success", command=add_item).grid(row=0, column=6, padx=15)

# --- MIDDLE SELECTION BODY ---
body_frame = ttk.Frame(billing_frame)
body_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

# Left: Available Services
left_frame = ttk.LabelFrame(body_frame, text="1. Select Services")
left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

columns = ("ID","Service","Price","GST %")
tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=CENTER, width=100)
tree.pack(fill=BOTH, expand=True)

def load_products():
    for row in tree.get_children(): tree.delete(row)
    df = pd.read_csv(PRODUCTS_FILE)
    for _, row in df.iterrows(): tree.insert("", END, values=list(row))

load_products()

# Center: Actions
action_frame = ttk.Frame(body_frame)
action_frame.pack(side=LEFT, fill=Y, padx=10, pady=50)

def add_to_selection():
    for item in tree.selection():
        values = tree.item(item)['values']
        selected_tree.insert("", END, values=values)

def remove_from_selection():
    for item in selected_tree.selection(): selected_tree.delete(item)

ttk.Button(action_frame, text="Add >>", bootstyle="success", command=add_to_selection).pack(pady=5)
ttk.Button(action_frame, text="<< Remove", bootstyle="danger", command=remove_from_selection).pack(pady=5)

# Middle-Right: Selected Items
sel_frame = ttk.LabelFrame(body_frame, text="2. Selection List")
sel_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=5)

selected_tree = ttk.Treeview(sel_frame, columns=columns, show="headings", height=12)
for col in columns:
    selected_tree.heading(col, text=col)
    selected_tree.column(col, anchor=CENTER, width=100)
selected_tree.pack(fill=BOTH, expand=True)

# Right: Preview
right_frame = ttk.LabelFrame(body_frame, text="3. Invoice Preview", width=350)
right_frame.pack(side=RIGHT, fill=Y, padx=5)
invoice_text = ttk.Text(right_frame, width=40, height=25, font=("Courier", 9))
invoice_text.pack(padx=10, pady=10)

# --- BOTTOM ACTION BAR ---
bottom_frame = ttk.LabelFrame(billing_frame, text="Checkout & Generate")
bottom_frame.pack(fill=X, padx=20, pady=10)

ttk.Label(bottom_frame, text="Name:").pack(side=LEFT, padx=5)
customer_entry = ttk.Entry(bottom_frame, width=15)
customer_entry.pack(side=LEFT, padx=5)

ttk.Label(bottom_frame, text="Address:").pack(side=LEFT, padx=5)
address_entry = ttk.Entry(bottom_frame, width=15)
address_entry.pack(side=LEFT, padx=5)

ttk.Label(bottom_frame, text="Contact:").pack(side=LEFT, padx=5)
contact_entry = ttk.Entry(bottom_frame, width=12)
contact_entry.pack(side=LEFT, padx=5)

last_invoice_path = None

def generate_invoice():
    global last_invoice_path
    children = selected_tree.get_children()
    if not children:
        messagebox.showwarning("Empty", "Please select services first")
        return
    customer = customer_entry.get()
    if not customer:
        messagebox.showwarning("Input", "Enter customer name")
        return

    df_existing = pd.read_csv(SALES_FILE)
    invoice_no = df_existing["invoice_no"].nunique() + 1001
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    selected_items_data = []
    grand_total = 0
    df = pd.read_csv(SALES_FILE)

    invoice_text.delete("1.0", END)
    invoice_text.insert(END, f"INVOICE NO: {invoice_no}\nCUSTOMER: {customer}\nDATE: {date}\n" + "-"*40 + "\n")

    for child in children:
        item = selected_tree.item(child)["values"]
        service, price, gst = item[1], float(item[2]), float(item[3])
        total = price + (price * gst / 100)
        grand_total += total
        selected_items_data.append([service, f"₹{price}", f"{gst}%", f"₹{total:.2f}"])
        df.loc[len(df)] = [invoice_no, date, customer, service, price, gst, total]
        invoice_text.insert(END, f"{service:<20} | ₹{total:>8.2f}\n")

    df.to_csv(SALES_FILE, index=False)
    invoice_text.insert(END, "-"*40 + f"\nGRAND TOTAL: ₹{grand_total:.2f}\n")

    from modules.invoice import generate_invoice_pdf
    generate_invoice_pdf(invoice_no, customer, selected_items_data, grand_total, address_entry.get(), contact_entry.get())
    last_invoice_path = os.path.join(INVOICE_FOLDER, f"Invoice_{invoice_no}.pdf")
    
    for child in children: selected_tree.delete(child)
    messagebox.showinfo("Success", f"Invoice #{invoice_no} Generated!")

ttk.Button(bottom_frame, text="Save & PDF", bootstyle="primary", command=generate_invoice).pack(side=LEFT, padx=10)

def print_invoice():
    if last_invoice_path and os.path.exists(last_invoice_path):
        os.startfile(last_invoice_path, "print")
    else: messagebox.showwarning("Error", "Generate invoice first")

ttk.Button(bottom_frame, text="Print", bootstyle="secondary", command=print_invoice).pack(side=LEFT, padx=5)

def download_invoice():
    if not last_invoice_path:
        messagebox.showwarning("Error", "Generate invoice first")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=os.path.basename(last_invoice_path))
    if save_path:
        import shutil
        shutil.copy(last_invoice_path, save_path)
        messagebox.showinfo("Success", "File exported successfully!")

ttk.Button(bottom_frame, text="Download", bootstyle="success", command=download_invoice).pack(side=LEFT, padx=5)

def reset_billing():
    customer_entry.delete(0, END)
    address_entry.delete(0, END)
    contact_entry.delete(0, END)
    for child in selected_tree.get_children(): selected_tree.delete(child)
    invoice_text.delete("1.0", END)
    global last_invoice_path
    last_invoice_path = None

ttk.Button(bottom_frame, text="Reset", bootstyle="warning-outline", command=reset_billing).pack(side=LEFT, padx=10)

# ================== REPORTS TAB LOGIC ==================
filter_frame = ttk.LabelFrame(reports_frame, text="Date Range Filter")
filter_frame.pack(fill=X, padx=20, pady=10)

start_date_entry = ttk.Entry(filter_frame, width=15)
start_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
end_date_entry = ttk.Entry(filter_frame, width=15)
end_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

ttk.Label(filter_frame, text="From (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
start_date_entry.grid(row=0, column=1, padx=5)
ttk.Label(filter_frame, text="To (YYYY-MM-DD):").grid(row=0, column=2, padx=10)
end_date_entry.grid(row=0, column=3, padx=5)

# --- Stats Summary Table ---
summary_frame = ttk.LabelFrame(reports_frame, text="Financial Summary")
summary_frame.pack(fill=X, padx=20, pady=5)

summary_cols = ("Metric", "Value")
summary_tree = ttk.Treeview(summary_frame, columns=summary_cols, show="headings", height=6, bootstyle="info")
for col in summary_cols:
    summary_tree.heading(col, text=col)
    summary_tree.column(col, width=300, anchor=W if col=="Metric" else E)
summary_tree.pack(fill=X, padx=10, pady=10)

# --- Detailed Sales Table ---
sales_list_frame = ttk.LabelFrame(reports_frame, text="Detailed Sales History")
sales_list_frame.pack(fill=BOTH, expand=True, padx=20, pady=5)

sales_cols = ("Invoice #", "Date", "Customer", "Item", "Total")
sales_report_tree = ttk.Treeview(sales_list_frame, columns=sales_cols, show="headings", height=8)
for col in sales_cols:
    sales_report_tree.heading(col, text=col)
    sales_report_tree.column(col, width=150, anchor=CENTER)
sales_report_tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

def refresh_stats():
    try:
        sales = pd.read_csv(SALES_FILE)
        expenses = pd.read_csv(EXPENSES_FILE)
        
        # Clear existing
        for item in summary_tree.get_children(): summary_tree.delete(item)
        for item in sales_report_tree.get_children(): sales_report_tree.delete(item)

        if sales.empty:
            summary_tree.insert("", END, values=("Info", "No data found"))
            return

        # Date handling
        sales['date_dt'] = pd.to_datetime(sales['date']).dt.date
        expenses['date_dt'] = pd.to_datetime(expenses['date']).dt.date
        
        sd = datetime.strptime(start_date_entry.get(), "%Y-%m-%d").date()
        ed = datetime.strptime(end_date_entry.get(), "%Y-%m-%d").date()
        
        f_sales = sales[(sales['date_dt'] >= sd) & (sales['date_dt'] <= ed)]
        f_expenses = expenses[(expenses['date_dt'] >= sd) & (expenses['date_dt'] <= ed)]
        
        total_sales = f_sales["total"].sum()
        revenue_ex_gst = f_sales["price"].sum()
        gst_collected = total_sales - revenue_ex_gst
        total_exp = f_expenses["amount"].sum()
        profit = revenue_ex_gst - total_exp
        
        # Populate Summary Table
        metrics = [
            ("Total Sales (Incl. GST)", f"₹ {total_sales:,.2f}"),
            ("Total Revenue (Excl. GST)", f"₹ {revenue_ex_gst:,.2f}"),
            ("GST Collected", f"₹ {gst_collected:,.2f}"),
            ("Total Expenses", f"₹ {total_exp:,.2f}"),
            ("NET PROFIT/LOSS", f"₹ {profit:,.2f}")
        ]
        for m, v in metrics:
            summary_tree.insert("", END, values=(m, v))
            if "PROFIT" in m:
                item_id = summary_tree.get_children()[-1]
                summary_tree.tag_configure("gain", foreground="green" if profit >=0 else "red")
                summary_tree.item(item_id, tags=("gain",))

        # Populate Detailed Table
        for _, row in f_sales.iterrows():
            sales_report_tree.insert("", END, values=(
                row["invoice_no"], row["date"], row["customer"], row["service"], f"₹{row['total']:.2f}"
            ))
        
    except Exception as e:
        messagebox.showerror("Error", f"Could not calculate stats: {e}")

ttk.Button(filter_frame, text="Refresh Stats", bootstyle="info", command=refresh_stats).grid(row=0, column=4, padx=20)

def download_report_pdf():
    try:
        from modules.reports_pdf import generate_financial_report_pdf
        from modules.paths import INVOICE_FOLDER
        
        sd = start_date_entry.get()
        ed = end_date_entry.get()
        
        # Get data from tables
        summary_data = []
        for child in summary_tree.get_children():
            summary_data.append(summary_tree.item(child)["values"])
            
        sales_data = []
        for child in sales_report_tree.get_children():
            sales_data.append(sales_report_tree.item(child)["values"])
            
        if not sales_data:
            messagebox.showwarning("Empty", "No data to export for the selected range.")
            return

        temp_path = os.path.join(INVOICE_FOLDER, f"Financial_Report_{sd}_to_{ed}.pdf")
        generate_financial_report_pdf(temp_path, sd, ed, summary_data, sales_data)
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(temp_path)
        )
        
        if save_path:
            import shutil
            shutil.copy(temp_path, save_path)
            messagebox.showinfo("Success", "Financial Report exported successfully!")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export report: {e}")

ttk.Button(filter_frame, text="⬇️ Download Report PDF", bootstyle="success-outline", command=download_report_pdf).grid(row=0, column=5, padx=10)

# Delete Section in Reports (Optional)
del_frame = ttk.LabelFrame(reports_frame, text="Danger Zone")
del_frame.pack(fill=X, padx=20, pady=10)
ttk.Label(del_frame, text="Remove Invoice No:").pack(side=LEFT, padx=10)
del_inv_entry = ttk.Entry(del_frame, width=10)
del_inv_entry.pack(side=LEFT, padx=5)

def delete_inv_action():
    try:
        inv = int(del_inv_entry.get())
        df = pd.read_csv(SALES_FILE)
        df = df[df["invoice_no"] != inv]
        df.to_csv(SALES_FILE, index=False)
        messagebox.showinfo("Success", f"Invoice #{inv} removed")
        refresh_stats()
    except: messagebox.showwarning("Error", "Invalid Invoice Number")

ttk.Button(del_frame, text="Delete Data", bootstyle="danger-outline", command=delete_inv_action).pack(side=LEFT, padx=15)

# ================== BALANCE SHEET TAB LOGIC ==================
bs_header = ttk.Frame(balance_sheet_frame)
bs_header.pack(fill=X, padx=20, pady=20)

ttk.Label(bs_header, text="Business Balance Sheet Snapshot", font=("Helvetica", 18, "bold")).pack(side=LEFT)

def refresh_balance_sheet():
    try:
        sales = pd.read_csv(SALES_FILE)
        expenses = pd.read_csv(EXPENSES_FILE)
        
        total_sales_inc_gst = sales["total"].sum()
        revenue_ex_gst = sales["price"].sum()
        gst_collected = total_sales_inc_gst - revenue_ex_gst
        total_exp = expenses["amount"].sum()
        
        cash_balance = total_sales_inc_gst - total_exp
        gst_payable = gst_collected
        retained_earnings = revenue_ex_gst - total_exp
        
        # Update UI Labels
        cash_val_lbl.config(text=f"₹ {cash_balance:,.2f}")
        gst_val_lbl.config(text=f"₹ {gst_payable:,.2f}")
        equity_val_lbl.config(text=f"₹ {retained_earnings:,.2f}")
        
        total_assets_lbl.config(text=f"Total Assets: ₹ {cash_balance:,.2f}")
        total_liab_eq_lbl.config(text=f"Total Liabilities & Equity: ₹ {gst_payable + retained_earnings:,.2f}")
        
    except Exception as e:
        messagebox.showerror("Error", f"Balance Sheet calculation failed: {e}")

def download_bs_pdf():
    try:
        from modules.reports_pdf import generate_balance_sheet_pdf
        from modules.paths import INVOICE_FOLDER
        
        # Parse currency strings back to floats
        def parse_curr(s):
            return float(s.replace('₹', '').replace(',', '').strip())
        
        cash = parse_curr(cash_val_lbl.cget("text"))
        gst = parse_curr(gst_val_lbl.cget("text"))
        equity = parse_curr(equity_val_lbl.cget("text"))

        temp_path = os.path.join(INVOICE_FOLDER, f"Balance_Sheet_{datetime.now().strftime('%Y-%m-%d')}.pdf")
        generate_balance_sheet_pdf(temp_path, cash, gst, equity)
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(temp_path)
        )
        
        if save_path:
            import shutil
            shutil.copy(temp_path, save_path)
            messagebox.showinfo("Success", "Balance Sheet exported successfully!")
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export balance sheet: {e}")

ttk.Button(bs_header, text="⬇️ Download Balance Sheet PDF", bootstyle="success-outline", command=download_bs_pdf).pack(side=RIGHT, padx=10)
ttk.Button(bs_header, text="🔄 Refresh Balance Sheet", bootstyle="info", command=refresh_balance_sheet).pack(side=RIGHT)

bs_body = ttk.Frame(balance_sheet_frame)
bs_body.pack(fill=BOTH, expand=True, padx=20)

# --- Assets Column ---
assets_frame = ttk.LabelFrame(bs_body, text="ASSETS")
assets_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

ttk.Label(assets_frame, text="Current Assets", font=("Helvetica", 12, "bold")).pack(anchor=W, padx=10, pady=10)
cash_row = ttk.Frame(assets_frame)
cash_row.pack(fill=X, padx=20, pady=5)
ttk.Label(cash_row, text="Cash & Bank Balance:", font=("Helvetica", 11)).pack(side=LEFT)
cash_val_lbl = ttk.Label(cash_row, text="₹ 0.00", font=("Helvetica", 11, "bold"))
cash_val_lbl.pack(side=RIGHT)

ttk.Separator(assets_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=20)
total_assets_lbl = ttk.Label(assets_frame, text="Total Assets: ₹ 0.00", font=("Helvetica", 12, "bold"))
total_assets_lbl.pack(anchor=E, padx=10)

# --- Liabilities & Equity Column ---
liab_frame = ttk.LabelFrame(bs_body, text="LIABILITIES & EQUITY")
liab_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

ttk.Label(liab_frame, text="Liabilities", font=("Helvetica", 12, "bold")).pack(anchor=W, padx=10, pady=10)
gst_row = ttk.Frame(liab_frame)
gst_row.pack(fill=X, padx=20, pady=5)
ttk.Label(gst_row, text="GST Payable (Collected):", font=("Helvetica", 11)).pack(side=LEFT)
gst_val_lbl = ttk.Label(gst_row, text="₹ 0.00", font=("Helvetica", 11, "bold"))
gst_val_lbl.pack(side=RIGHT)

ttk.Label(liab_frame, text="Equity", font=("Helvetica", 12, "bold")).pack(anchor=W, padx=10, pady=(30, 10))
equity_row = ttk.Frame(liab_frame)
equity_row.pack(fill=X, padx=20, pady=5)
ttk.Label(equity_row, text="Retained Earnings (Profit):", font=("Helvetica", 11)).pack(side=LEFT)
equity_val_lbl = ttk.Label(equity_row, text="₹ 0.00", font=("Helvetica", 11, "bold"))
equity_val_lbl.pack(side=RIGHT)

ttk.Separator(liab_frame, orient=HORIZONTAL).pack(fill=X, padx=10, pady=20)
total_liab_eq_lbl = ttk.Label(liab_frame, text="Total Liabilities & Equity: ₹ 0.00", font=("Helvetica", 12, "bold"))
total_liab_eq_lbl.pack(anchor=E, padx=10)

# Initialize data
refresh_stats()
refresh_balance_sheet()

app.mainloop()
