"""
Export SoundCraft Musical Instruments Catalog into:
1. instruments_list.docx (Formatted Microsoft Word document with tables)
2. instruments_list.csv (Excel spreadsheet)
3. instruments_list.txt (Plain text table)
"""

import os
import csv
import shutil
import database
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def export_all():
    items = database.get_all_instruments()
    print(f"Total instruments to export: {len(items)}")

    # 1. CSV
    csv_file = "instruments_list.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Instrument Name", "Category", "Brand", "Price (INR)", "Stock", "Status"])
        for i in items:
            status = "In Stock" if i['quantity'] > 5 else ("Low Stock" if i['quantity'] > 0 else "Out of Stock")
            writer.writerow([i['instrument_id'], i['name'], i['category'], i['brand'], f"{i['price']:.2f}", i['quantity'], status])
    print(f"[OK] Created {csv_file}")

    # 2. TXT
    txt_file = "instruments_list.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("="*90 + "\n")
        f.write("                   SOUNDCRAFT MUSICAL INSTRUMENT INVENTORY\n")
        f.write("                             COMPLETE CATALOG\n")
        f.write("="*90 + "\n\n")
        f.write(f"Total Instruments : {len(items)}\n")
        f.write(f"Catalog Currency  : INR (Rs.)\n\n")
        f.write("-" * 90 + "\n")
        f.write(f"{'ID':<8} | {'Instrument Name':<34} | {'Category':<24} | {'Brand':<12} | {'Price':<11} | {'Stock'}\n")
        f.write("-" * 90 + "\n")
        for i in items:
            f.write(f"{i['instrument_id']:<8} | {i['name']:<34} | {i['category']:<24} | {i['brand']:<12} | Rs.{i['price']:<8.2f} | {i['quantity']}\n")
        f.write("-" * 90 + "\n")
    print(f"[OK] Created {txt_file}")

    # 3. DOCX
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)

    title_p = doc.add_paragraph()
    r = title_p.add_run("SoundCraft Musical Instruments")
    r.font.name = "Segoe UI"
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 23, 42)

    sub_p = doc.add_paragraph()
    r2 = sub_p.add_run("Official Instrument Catalog & Stock Inventory List")
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(13)
    r2.font.bold = True
    r2.font.color.rgb = RGBColor(79, 70, 229)

    meta_p = doc.add_paragraph()
    r3 = meta_p.add_run(f"Total Registered Instruments: {len(items)}  |  Currency: INR (Rs.)  |  Status: Verified Active")
    r3.font.name = "Segoe UI"
    r3.font.size = Pt(9.5)
    r3.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    categories = {}
    for i in items:
        cat = i['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(i)

    col_widths = [Inches(1.0), Inches(2.4), Inches(1.2), Inches(1.2), Inches(0.9)]

    for cat_name, cat_items in categories.items():
        h = doc.add_heading(level=2)
        hr = h.add_run(f"{cat_name} ({len(cat_items)} Items)")
        hr.font.name = "Segoe UI"
        hr.font.size = Pt(13)
        hr.font.color.rgb = RGBColor(30, 41, 59)

        table = doc.add_table(rows=1, cols=5)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        hdr_cells = table.rows[0].cells
        headers = ["ID", "Instrument Name", "Brand", "Price (INR)", "Stock"]
        for idx, text in enumerate(headers):
            hdr_cells[idx].text = text
            hdr_cells[idx].width = col_widths[idx]
            shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="4F46E5"/>')
            hdr_cells[idx]._tc.get_or_add_tcPr().append(shd)
            p = hdr_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9.5)

        for row_idx, item in enumerate(cat_items):
            row_cells = table.add_row().cells
            stock_str = f"{item['quantity']} units" if item['quantity'] > 0 else "Out of Stock"
            vals = [
                str(item['instrument_id']),
                str(item['name']),
                str(item['brand']),
                f"Rs.{item['price']:,.2f}",
                stock_str
            ]
            bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(vals):
                row_cells[c_idx].text = val
                row_cells[c_idx].width = col_widths[c_idx]
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_color}"/>')
                row_cells[c_idx]._tc.get_or_add_tcPr().append(shd)
                p = row_cells[c_idx].paragraphs[0]
                if c_idx in [0, 3, 4]:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.size = Pt(9)
                    run.font.name = "Segoe UI"
                    if c_idx == 4 and item['quantity'] == 0:
                        run.font.color.rgb = RGBColor(220, 38, 38)
                        run.font.bold = True

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

    docx_file = "instruments_list.docx"
    doc.save(docx_file)
    print(f"[OK] Created {docx_file}")

    # Copy to Desktop
    desktop = os.path.expanduser("~/Desktop")
    if os.path.exists(desktop):
        shutil.copy(docx_file, os.path.join(desktop, docx_file))
        shutil.copy(csv_file, os.path.join(desktop, csv_file))
        shutil.copy(txt_file, os.path.join(desktop, txt_file))
        print(f"[OK] Successfully copied to Desktop: {desktop}")

if __name__ == "__main__":
    export_all()
