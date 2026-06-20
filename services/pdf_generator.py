from fpdf import FPDF

def generate_pdf(
    disease,
    risk,
    report
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(
        0,
        10,
        f"""
Disease: {disease}

Risk: {risk}

Report:

{report}
"""
    )

    path = "reports/report.pdf"

    pdf.output(path)

    return path