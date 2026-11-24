
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from document_processor import process_document
from question_processor import process_question


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def home():

    answer = None
    filename = None
    question = ""
    error = None

    if request.method == "POST":

        file = request.files.get("document")
        question = request.form.get("question", "").strip()

        if not file or file.filename == "":
            error = "Please upload a document."

        elif not allowed_file(file.filename):
            error = "Please upload a PDF, DOCX, or TXT file."

        elif not question:
            error = "Please enter your question."

        else:
            filename = secure_filename(file.filename)

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"], filename
            )

            file.save(file_path)

            document_text, processing_error = process_document(file_path)

            if processing_error:
                error = processing_error
            else:
                answer = process_question(question, document_text)

    return render_template(
        "index.html",
        answer=answer,
        filename=filename,
        question=question,
        error=error
    )


if __name__ == "__main__":
    app.run(debug=True)
