import io
import pypdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts plain text from PDF file bytes.
    """
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def generate_pdf_report(title: str, content: str) -> bytes:
    """
    Generates a simple PDF report from a title and body text, returns raw bytes.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)

    c.setFont("Helvetica", 11)
    text_obj = c.beginText(50, height - 90)
    text_obj.setLeading(16)

    for line in content.split("\n"):
        # naive wrap at ~90 chars so long lines don't run off the page
        while len(line) > 90:
            text_obj.textLine(line[:90])
            line = line[90:]
        text_obj.textLine(line)

    c.drawText(text_obj)
    c.save()

    buffer.seek(0)
    return buffer.read()




def extract_text_from_xlsx(file_bytes: bytes) -> str:
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    text_parts = []
    for sheet in wb.worksheets:
        text_parts.append(f"Sheet: {sheet.title}")
        for row in sheet.iter_rows(values_only=True):
            row_text = "\t".join(str(cell) if cell is not None else "" for cell in row)
            if row_text.strip():
                text_parts.append(row_text)
    return "\n".join(text_parts)