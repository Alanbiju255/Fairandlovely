from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import pandas as pd
import os

from modules.paths import INVOICE_FOLDER, SALES_FILE as DATA_FILE

# ===============================
# GENERATE INVOICE PDF (REDESIGNED)
# ===============================
def generate_invoice_pdf(invoice_no, customer, items, total, address="", contact=""):
    filename = os.path.join(INVOICE_FOLDER, f"Invoice_{invoice_no}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles['Title'].fontSize = 28
    styles['Title'].alignment = 2 # Right
    styles['Heading1'].fontSize = 14
    
    # --- 1. HEADER SECTION (Business Info vs "INVOICE") ---
    business_info = [
        [Paragraph("<b>Fairandlovely</b><br/>Opp P.O junction , MUVATTUPUZHA<br/>Phone: +91 9495126954", styles['Normal']),
         Paragraph("INVOICE", styles['Title'])]
    ]
    header_table = Table(business_info, colWidths=[3.5*inch, 3*inch])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)
    elements.append(Spacer(1, 40))

    # --- 2. INFORMATION SECTION (Customer vs Invoice Info) ---
    info_data = [
        [Paragraph(f"<b>BILL TO:</b><br/>{customer}<br/>{address if address else 'No Address Provided'}<br/>Contact: {contact if contact else 'Not Provided'}", styles['Normal']),
         Table([
             ["Invoice #", str(invoice_no)],
             ["Invoice Date", datetime.now().strftime('%m/%d/%Y')],
             ["Due Date", datetime.now().strftime('%m/%d/%Y')]
         ], colWidths=[1.2*inch, 1*inch])]
    ]
    info_table = Table(info_data, colWidths=[4*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('GRID', (1,0), (1,0), 0.5, colors.white), # Invisible grid for spacing
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))

    # --- 3. ITEMS TABLE ---
    # Header for items table
    data = [["Service Description", "Unit Price", "GST %", "Quantity", "Amount"]]
    
    # Convert input items to match table format (Assuming Quantity 1 for now)
    subtotal_base = 0
    for item in items:
        # items format from main.py: [service, price_str, gst_str, total_str]
        try:
            name = item[0]
            price_val = float(item[1].replace('₹','').replace(',',''))
            subtotal_base += price_val
            data.append([name, item[1], item[2], "1.00", item[3]])
        except:
            data.append([item[0], item[1], item[2], "1.00", item[3]])

    items_table = Table(data, colWidths=[2.8*inch, 1.1*inch, 0.8*inch, 0.8*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'), # Price
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),# GST % and Quantity
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'), # Amount
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")])
    ]))
    elements.append(items_table)
    
    # Notes area (like in the image)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>NOTES:</b> Thank you for your business. Taxes are included in the final total.", styles['Normal']))
    elements.append(Spacer(1, 20))

    # --- 4. SUMMARY SECTION ---
    gst_amt = total - subtotal_base
    summary_data = [
        ["", "Subtotal (Base)", f"₹ {subtotal_base:,.2f}"],
        ["", "GST Amount", f"₹ {gst_amt:,.2f}"],
        ["", "Total", f"₹ {total:,.2f}"],
        ["", "Amount Paid", "0.00"],
        ["", "Balance Due", f"₹ {total:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[4.3*inch, 1.2*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1,0), (-1,-1), 'LEFT'),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (1,3), (2,3), 'Helvetica-Bold'),
        ('BACKGROUND', (1,3), (2,3), colors.HexColor("#EEEEEE")),
        ('LINEABOVE', (1,1), (2,1), 1, colors.black),
        ('LINEBELOW', (1,3), (2,3), 1, colors.black),
        ('GRID', (1,0), (2,3), 0.1, colors.grey),
    ]))
    elements.append(summary_table)

    doc.build(elements)
    return filename

def delete_invoice(invoice_no):
    invoice_no = int(invoice_no)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = df[df["invoice_no"] != invoice_no]
        df.to_csv(DATA_FILE, index=False)
    pdf_path = os.path.join(INVOICE_FOLDER, f"Invoice_{invoice_no}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    return True
