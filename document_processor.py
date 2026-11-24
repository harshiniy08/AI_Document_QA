
import os
from PyPDF2 import PdfReader
from docx import Document


def process_document(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if extension == ".pdf":
            reader = PdfReader(file_path)

            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"

        elif extension == ".docx":
            document = Document(file_path)

            for paragraph in document.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"

            for table in document.tables:
                for row in table.rows:
                    text += " | ".join(
                        cell.text for cell in row.cells
                    ) + "\n"

        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

        else:
            return None, "Unsupported file format."

        if not text.strip():
            return None, "No readable text found in the document."

        return text.strip(), None

    except Exception as error:
        return None, str(error)
