from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
import os

def generate_financial_report_pdf(path, start_date, end_date, summary_data, sales_data):
    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Fairandlovely - FINANCIAL REPORT</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # Info
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Paragraph(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 18))

    # Summary Table
    elements.append(Paragraph("<b>Financial Summary</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))
    
    summary_table_data = [["Metric", "Value"]]
    for m, v in summary_data:
        summary_table_data.append([m, v])

    s_table = Table(summary_table_data, colWidths=[3*72, 1.5*72])
    s_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(s_table)
    elements.append(Spacer(1, 24))

    # Detailed Sales
    elements.append(Paragraph("<b>Detailed Sales History</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    sales_table_data = [["Invoice #", "Date", "Customer", "Item", "Total"]]
    for row in sales_data:
        sales_table_data.append(row)

    d_table = Table(sales_table_data, colWidths=[0.8*72, 1.2*72, 1.2*72, 1.2*72, 0.8*72])
    d_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(d_table)

    doc.build(elements)
    return path

def generate_balance_sheet_pdf(path, cash, gst_payable, equity):
    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Fairandlovely - BALANCE SHEET</b>", styles['Title']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"As of: {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 24))

    # Assets & Liabilities Comparison
    data = [
        ["ASSETS", "", "LIABILITIES & EQUITY", ""],
        ["Current Assets", "", "Liabilities", ""],
        ["  Cash & Bank Balance", f"₹ {cash:,.2f}", "  GST Payable", f"₹ {gst_payable:,.2f}"],
        ["", "", "Equity", ""],
        ["", "", "  Retained Earnings", f"₹ {equity:,.2f}"],
        ["", "", "", ""],
        [f"TOTAL ASSETS", f"₹ {cash:,.2f}", f"TOTAL LIAB. & EQUITY", f"₹ {gst_payable + equity:,.2f}"]
    ]

    table = Table(data, colWidths=[1.5*72, 1*72, 1.5*72, 1*72])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgreen),
        ('BACKGROUND', (2, 0), (3, 0), colors.lightpink),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('GRID', (2, 0), (3, -1), 1, colors.black),
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (2, 0), (3, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("<i>This is a computer-generated financial statement.</i>", styles['Italic']))

    doc.build(elements)
    return path
