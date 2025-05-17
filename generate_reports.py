from fpdf import FPDF
import csv
import os

def generate_pdf(report_data, file_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resume Analysis Report", ln=True, align='C')
    pdf.ln(10)
    for key, value in report_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    pdf.output(file_path)

def generate_csv(report_data, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Field", "Value"])
        for key, value in report_data.items():
            writer.writerow([key, value])

def save_report(data, file_name, format):
    if format == 'pdf':
        generate_pdf(data, os.path.join('reports', file_name + '.pdf'))
    elif format == 'csv':
        generate_csv(data, os.path.join('reports', file_name + '.csv'))
