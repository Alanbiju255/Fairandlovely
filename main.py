import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time

# --- PANDAS SETTINGS ---
pd.options.display.float_format = '{:,.2f}'.format

# --- MODULE IMPORTS ---
try:
    from modules.paths import PRODUCTS_FILE, SALES_FILE, EXPENSES_FILE, INVOICE_FOLDER
    from modules.invoice import generate_invoice_pdf
    from modules.reports_pdf import generate_financial_report_pdf, generate_balance_sheet_pdf
except ImportError:
    st.error("Modules not found. Ensure 'modules' directory exists.")
    st.stop()

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Fairandlovely - Management System",
    page_icon="logo.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR MODERN DARK THEME ---
st.markdown("""
<style>
    /* Global Font Adjustment */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    
    /* Buttons Customization (Optional overrides, Streamlit theme handles most) */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    
    /* Success/Primary Button specific if needed */
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: #1E1E1E;
        color: white;
        border-radius: 5px;
    }
    
    /* Table Header Styling */
    thead tr th:first-child { display:none }
    tbody th { display:none }
    
    /* Hide index in tables generally (Streamlit does this via hide_index=True usually) */
</style>
""", unsafe_allow_html=True)

# --- INITIALIZATION ---
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'last_invoice' not in st.session_state:
    st.session_state.last_invoice = None

# Ensure Files Exist
def init_files():
    if not os.path.exists(PRODUCTS_FILE) or os.path.getsize(PRODUCTS_FILE) == 0:
        pd.DataFrame(columns=["id","name","price","gst"]).to_csv(PRODUCTS_FILE, index=False)
    if not os.path.exists(SALES_FILE) or os.path.getsize(SALES_FILE) == 0:
        pd.DataFrame(columns=["invoice_no","date","customer","service","price","gst","total"]).to_csv(SALES_FILE, index=False)
    if not os.path.exists(EXPENSES_FILE) or os.path.getsize(EXPENSES_FILE) == 0:
        pd.DataFrame(columns=["date","description","amount"]).to_csv(EXPENSES_FILE, index=False)

init_files()

# --- HELPER FUNCTIONS ---
def load_data(file):
    try:
        return pd.read_csv(file)
    except:
        return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    if os.path.exists("logo.ico"):
        st.image("logo.ico", width=100) # Display logo if available
    st.title("Fairandlovely")
    st.markdown("---")
    menu = st.radio("Navigation", ["📝 Billing", "📊 Reports", "🏢 Balance Sheet"], index=0)
    st.markdown("---")
    st.caption("v2.0 | Streamlit Edition")

# --- PAGE: BILLING ---
if menu == "📝 Billing":
    st.title("📝 Billing & Invoicing")
    
    # 1. Add New Item (Expander to save space)
    with st.expander("➕ Add New Service/Item to Menu"):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        with c1: new_name = st.text_input("Service Name")
        with c2: new_price = st.number_input("Price (₹)", min_value=0.0, step=10.0)
        with c3: new_gst = st.number_input("GST %", min_value=0.0, max_value=28.0, step=1.0)
        with c4:
            st.write("") # Spacer
            st.write("") # Spacer
            if st.button("Add to Menu", type="primary"):
                if new_name:
                    df = load_data(PRODUCTS_FILE)
                    new_id = len(df) + 1
                    new_row = {"id": new_id, "name": new_name, "price": new_price, "gst": new_gst}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_data(df, PRODUCTS_FILE)
                    st.success(f"Added {new_name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Name required")

    # 2. Billing Area
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.subheader("1. Select Services")
        products_df = load_data(PRODUCTS_FILE)
        
        if not products_df.empty:
            # Custom formatting for display
            products_df['display'] = products_df.apply(lambda x: f"{x['name']} (₹{x['price']})", axis=1)
            
            # Use columns for layout
            row1 = st.columns([3, 1])
            with row1[0]:
                selected_product_name = st.selectbox("Search Service", products_df['display'].tolist(), index=None, placeholder="Type to search...")
            with row1[1]:
                 if st.button("Add to Cart ➡️", type="primary", use_container_width=True):
                    if selected_product_name:
                        # Find the product
                        prod = products_df[products_df['display'] == selected_product_name].iloc[0]
                        # Add to session state cart
                        # Structure: [name, price, gst, total_with_gst]
                        price = float(prod['price'])
                        gst = float(prod['gst'])
                        total = price + (price * gst / 100)
                        item = {
                            "id": prod['id'],
                            "name": prod['name'],
                            "price": price,
                            "gst": gst,
                            "total": total
                        }
                        st.session_state.cart.append(item)
                        st.success(f"Added {prod['name']}")
                        # time.sleep(0.1) # Optional UI feedback
                        st.rerun()
                    else:
                        st.warning("Select a service first")
        
        st.markdown("### Cart Items")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            
            # Display readable cart
            st.dataframe(
                cart_df[["name", "price", "gst", "total"]], 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "name": "Service",
                    "price": st.column_config.NumberColumn("Price (₹)", format="₹ %.2f"),
                    "gst": st.column_config.NumberColumn("GST %", format="%.0f%%"),
                    "total": st.column_config.NumberColumn("Total (₹)", format="₹ %.2f"),
                }
            )
            
            if st.button("🗑️ Clear Cart", type="secondary"):
                st.session_state.cart = []
                st.rerun()
        else:
            st.info("Cart is empty. Add items from above.")

    with col_right:
        st.subheader("2. Checkout Details")
        with st.container(border=True):
            cust_name = st.text_input("Customer Name *")
            cust_addr = st.text_input("Address")
            cust_contact = st.text_input("Contact")
            
            st.markdown("---")
            
            # Calculate Totals
            grand_total = sum(item['total'] for item in st.session_state.cart)
            sub_total = sum(item['price'] for item in st.session_state.cart)
            gst_total = grand_total - sub_total
            
            # Invoice Summary
            st.markdown(f"""
            <div style="text-align: right; font-size: 1.1em;">
                <p>Subtotal: <b>₹ {sub_total:,.2f}</b></p>
                <p>GST: <b>₹ {gst_total:,.2f}</b></p>
                <h3 style="color: #4CAF50;">Total: ₹ {grand_total:,.2f}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✅ Generate Invoice & PDF", type="primary", use_container_width=True):
                if not st.session_state.cart:
                    st.error("Cart is empty!")
                elif not cust_name:
                    st.error("Customer Name is required!")
                else:
                    # Generate Invoice Process
                    sales_df = load_data(SALES_FILE)
                    
                    # Determine Invoice No
                    if not sales_df.empty:
                        last_inv_no = sales_df["invoice_no"].max()
                        # Handle potential NaN or non-numeric if legacy data exists, simplifying assumption:
                        try:
                            inv_no = int(last_inv_no) + 1
                        except:
                            inv_no = 1001
                    else:
                        inv_no = 1001
                        
                    inv_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Prepare Data for PDF & CSV
                    pdf_items = []
                    new_rows = []
                    
                    for item in st.session_state.cart:
                        # CSV Record
                        new_rows.append({
                            "invoice_no": inv_no,
                            "date": inv_date,
                            "customer": cust_name,
                            "service": item['name'],
                            "price": item['price'],
                            "gst": item['gst'],
                            "total": item['total']
                        })
                        # PDF Record: [service, price_str, gst_str, total_str]
                        pdf_items.append([
                            item['name'],
                            f"₹{item['price']:.2f}",
                            f"{item['gst']}%",
                            f"₹{item['total']:.2f}"
                        ])
                    
                    # Update Sales File
                    sales_df = pd.concat([sales_df, pd.DataFrame(new_rows)], ignore_index=True)
                    save_data(sales_df, SALES_FILE)
                    
                    # Generate PDF
                    try:
                        pdf_path = generate_invoice_pdf(inv_no, cust_name, pdf_items, grand_total, cust_addr, cust_contact)
                        st.session_state.last_invoice = pdf_path
                        st.session_state.cart = [] # Clear cart
                        st.success(f"Invoice #{inv_no} Generated Successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")

            # Download Button (if invoice generated)
            if st.session_state.last_invoice and os.path.exists(st.session_state.last_invoice):
                with open(st.session_state.last_invoice, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Invoice PDF",
                        data=pdf_file,
                        file_name=os.path.basename(st.session_state.last_invoice),
                        mime="application/pdf",
                        type="secondary",
                        use_container_width=True
                    )

# --- PAGE: REPORTS ---
elif menu == "📊 Reports":
    st.title("📊 Reports & Analytics")
    
    # Filter Section
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", value=date.today())
        with col2:
            end_date = st.date_input("End Date", value=date.today())
        with col3:
            st.write("") # Spacer
            if st.button("Apply Filter", type="primary", use_container_width=True):
                st.rerun()

    # Load Data
    sales_df = load_data(SALES_FILE)
    expenses_df = load_data(EXPENSES_FILE)

    if not sales_df.empty:
        # Date Conversion
        sales_df['date_dt'] = pd.to_datetime(sales_df['date']).dt.date
        filter_mask = (sales_df['date_dt'] >= start_date) & (sales_df['date_dt'] <= end_date)
        filtered_sales = sales_df[filter_mask]
        
        # Calculate Metrics
        total_sales = filtered_sales['total'].sum()
        revenue_ex_gst = filtered_sales['price'].sum()
        gst_collected = total_sales - revenue_ex_gst
        
        # Expenses (Assuming similar date structure if available, else standard)
        if not expenses_df.empty:
            try:
                expenses_df['date_dt'] = pd.to_datetime(expenses_df['date']).dt.date
                filtered_expenses = expenses_df[(expenses_df['date_dt'] >= start_date) & (expenses_df['date_dt'] <= end_date)]
                total_expenses = filtered_expenses['amount'].sum()
            except:
                total_expenses = 0.0
        else:
            total_expenses = 0.0
            
        net_profit = revenue_ex_gst - total_expenses
        
        # Display Metrics
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Sales", f"₹ {total_sales:,.0f}")
        m2.metric("Revenue (Ex GST)", f"₹ {revenue_ex_gst:,.0f}")
        m3.metric("GST Collected", f"₹ {gst_collected:,.0f}")
        m4.metric("Expenses", f"₹ {total_expenses:,.0f}")
        m5.metric("Net Profit", f"₹ {net_profit:,.0f}", delta_color="normal")

        st.markdown("---")
        
        # Charts Area
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Sales Trend")
            if not filtered_sales.empty:
                # Group by date
                daily_sales = filtered_sales.groupby('date_dt')['total'].sum().reset_index()
                st.bar_chart(daily_sales, x='date_dt', y='total', color="#4CAF50")
            else:
                st.info("No sales in selected range.")

        with c2:
            st.subheader("Top Services")
            if not filtered_sales.empty:
                top_services = filtered_sales['service'].value_counts().head(5)
                st.bar_chart(top_services, horizontal=True)
                
        # Detailed Data Table
        st.subheader("Detailed Sales History")
        st.dataframe(
            filtered_sales[['invoice_no', 'date', 'customer', 'service', 'total']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "invoice_no": "Inv #",
                "total": st.column_config.NumberColumn("Amount", format="₹ %.2f")
            }
        )
        
        # Download Report PDF
        if st.button("⬇️ Download Financial Report (PDF)"):
            try:
                # Prepare data for PDF module
                # Summary Data
                summary_data = [
                    ["Total Sales (Incl. GST)", f"₹ {total_sales:,.2f}"],
                    ["Total Revenue (Excl. GST)", f"₹ {revenue_ex_gst:,.2f}"],
                    ["GST Collected", f"₹ {gst_collected:,.2f}"],
                    ["Total Expenses", f"₹ {total_expenses:,.2f}"],
                    ["NET PROFIT/LOSS", f"₹ {net_profit:,.2f}"]
                ]
                # Sales Data
                sales_data_list = filtered_sales[['invoice_no', 'date', 'customer', 'service', 'total']].values.tolist()
                # Format total in list
                final_sales_data = []
                for row in sales_data_list:
                    # row: [inv, date, cust, service, total]
                    final_sales_data.append([row[0], row[1], row[2], row[3], f"₹{row[4]:.2f}"])

                report_path = os.path.join(INVOICE_FOLDER, f"Financial_Report_{start_date}_to_{end_date}.pdf")
                generate_financial_report_pdf(report_path, str(start_date), str(end_date), summary_data, final_sales_data)
                
                with open(report_path, "rb") as f:
                    st.download_button(
                        label="Download PDF Now",
                        data=f,
                        file_name=os.path.basename(report_path),
                        mime="application/pdf",
                        type="primary"
                    )
            except Exception as e:
                st.error(f"Failed to generate report: {e}")

    else:
        st.info("No sales data available.")

# --- PAGE: BALANCE SHEET ---
elif menu == "🏢 Balance Sheet":
    st.title("🏢 Business Balance Sheet")
    st.markdown("Snapshot of financial health.")

    sales_df = load_data(SALES_FILE)
    expenses_df = load_data(EXPENSES_FILE)
    
    if not sales_df.empty:
        total_sales_inc_gst = sales_df["total"].sum()
        revenue_ex_gst = sales_df["price"].sum()
        gst_collected = total_sales_inc_gst - revenue_ex_gst
    else:
        total_sales_inc_gst = 0.0
        revenue_ex_gst = 0.0
        gst_collected = 0.0
    
    if not expenses_df.empty:
        total_exp = expenses_df["amount"].sum()
    else:
        total_exp = 0.0
        
    cash_balance = total_sales_inc_gst - total_exp
    gst_payable = gst_collected
    retained_earnings = revenue_ex_gst - total_exp
    
    # Layout
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("ASSETS")
        with st.container(border=True):
            st.markdown("#### Current Assets")
            st.metric("Cash & Bank Balance", f"₹ {cash_balance:,.2f}")
            st.markdown("---")
            st.markdown(f"### Total Assets: ₹ {cash_balance:,.2f}")

    with c2:
        st.subheader("LIABILITIES & EQUITY")
        with st.container(border=True):
            st.markdown("#### Liabilities")
            st.metric("GST Payable", f"₹ {gst_payable:,.2f}")
            
            st.markdown("#### Equity")
            st.metric("Retained Earnings", f"₹ {retained_earnings:,.2f}")
            
            st.markdown("---")
            total_liab_equity = gst_payable + retained_earnings
            st.markdown(f"### Total Liab. & Equity: ₹ {total_liab_equity:,.2f}")
            
    # Download Balance Sheet
    st.markdown("### Export")
    if st.button("⬇️ Generate Balance Sheet PDF"):
        try:
            bs_path = os.path.join(INVOICE_FOLDER, f"Balance_Sheet_{date.today()}.pdf")
            generate_balance_sheet_pdf(bs_path, cash_balance, gst_payable, retained_earnings)
            with open(bs_path, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name=os.path.basename(bs_path),
                    mime="application/pdf",
                    type="primary"
                )
        except Exception as e:
            st.error(f"Error: {e}")
