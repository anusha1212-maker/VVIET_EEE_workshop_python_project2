import streamlit as st
from PyPDF2 import PdfMerger, PdfReader
from PIL import Image
from docx import Document
from reportlab.pdfgen import canvas
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Universal PDF Merger", layout="centered")
st.title("📄 Universal PDF Merger")

# ---------------- HELPERS ----------------

def convert_image_to_pdf(file):
    img = Image.open(file)
    if img.mode != "RGB":
        img = img.convert("RGB")

    pdf_bytes = io.BytesIO()
    img.save(pdf_bytes, format="PDF")
    pdf_bytes.seek(0)
    return pdf_bytes


def convert_docx_to_pdf(file):
    doc = Document(file)

    pdf_bytes = io.BytesIO()
    c = canvas.Canvas(pdf_bytes)

    y = 800
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            c.drawString(40, y, text)
            y -= 15

    c.save()
    pdf_bytes.seek(0)
    return pdf_bytes


def merge_all(files):
    merger = PdfMerger()

    for f in files:
        name = f.name.lower()

        try:
            if name.endswith(".pdf"):
                merger.append(f)

            elif name.endswith(("jpg", "jpeg", "png")):
                merger.append(convert_image_to_pdf(f))

            elif name.endswith(".docx"):
                merger.append(convert_docx_to_pdf(f))

        except Exception as e:
            st.warning(f"Skipped {f.name}: {e}")

    output = io.BytesIO()
    merger.write(output)
    output.seek(0)

    return output


def load_pdf(pdf_bytes):
    reader = PdfReader(pdf_bytes)
    return reader, len(reader.pages)


# ---------------- UI ----------------

uploaded_files = st.file_uploader(
    "Upload PDF, DOCX, or Image files",
    type=["pdf", "docx", "jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"{len(uploaded_files)} files ready")

    if st.button("🚀 Merge Files"):
        merged_pdf = merge_all(uploaded_files)
        st.session_state["merged_pdf"] = merged_pdf

        st.success("Merged successfully!")

        st.download_button(
            "⬇️ Download Merged PDF",
            data=merged_pdf,
            file_name="merged.pdf",
            mime="application/pdf"
        )

# ---------------- PREVIEW ----------------

if "merged_pdf" in st.session_state:
    st.subheader("📖 Preview")

    reader, total_pages = load_pdf(st.session_state["merged_pdf"])

    page_num = st.number_input(
        "Select Page",
        min_value=1,
        max_value=total_pages,
        step=1
    )

    page = reader.pages[page_num - 1]
    text = page.extract_text()

    st.write(f"### Page {page_num}")
    st.text(text if text else "No readable text (image-based content)")
