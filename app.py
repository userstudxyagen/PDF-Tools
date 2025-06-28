import streamlit as st
from utils.pdf_tools import merge_pdfs
import tempfile
import base64
import pdfplumber

st.set_page_config(page_title="PDF Tools", layout="centered")

# --- 💠 Custom CSS Style ---
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
    }

    .glass-container {
        backdrop-filter: blur(12px);
        background: rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        color: #000;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .glass-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 36px rgba(31, 38, 135, 0.2);
    }

    .card-btn {
        display: block;
        width: 100%;
        padding: 1rem;
        margin-bottom: 1rem;
        text-align: center;
        background-color: #ffffff10;
        border: 2px solid #ffffff30;
        border-radius: 14px;
        font-size: 1.2rem;
        color: #fff;
        backdrop-filter: blur(20px);
        cursor: pointer;
        transition: background 0.3s;
    }

    .card-btn:hover {
        background: #ffffff30;
    }

    .center {
        display: flex;
        justify-content: center;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .title {
        text-align: center;
        font-size: 2.5rem;
        margin-top: 1.5rem;
        font-weight: 700;
        color: #3366cc;
    }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ UI Layout ---
st.markdown("<h1 class='title'>📄 PDF Tool Web-App</h1>", unsafe_allow_html=True)

# --- 🧱 Tool Selection ---
st.markdown('<div class="center">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("📁 PDF anzeigen", key="viewer"):
        st.session_state["tool"] = "viewer"

    if st.button("📝 Text extrahieren", key="extract"):
        st.session_state["tool"] = "extract"

with col2:
    if st.button("🔗 PDF zusammenfügen", key="merge"):
        st.session_state["tool"] = "merge"

    if st.button("📄 Word zu PDF", key="word2pdf"):
        st.session_state["tool"] = "word2pdf"

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- 🧠 Tool Logic ---
tool = st.session_state.get("tool")

if tool == "viewer":
    st.subheader("📁 PDF anzeigen")
    pdf_file = st.file_uploader("PDF hochladen", type=["pdf"])
    if pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

elif tool == "merge":
    st.subheader("🔗 PDF zusammenfügen")
    pdf_files = st.file_uploader("PDF-Dateien hochladen", type=["pdf"], accept_multiple_files=True)
    if pdf_files:
        if st.button("📌 Jetzt zusammenfügen"):
            with st.spinner("Verarbeite PDFs..."):
                paths = []
                for pdf in pdf_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(pdf.read())
                        paths.append(tmp.name)
                result_path = merge_pdfs(paths)
                with open(result_path, "rb") as f:
                    st.download_button("📅 Herunterladen", f, file_name="merged.pdf")

elif tool == "extract":
    st.subheader("📝 Text aus PDF extrahieren")
    pdf_file = st.file_uploader("PDF-Datei hochladen", type=["pdf"])
    if pdf_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        st.text_area("📄 Extrahierter Text", text, height=300)

elif tool == "word2pdf":
    st.subheader("📄 Word zu PDF (Beta)")
    st.info("⚠️ Diese Funktion funktioniert nur lokal mit MS Word installiert.")
    word_file = st.file_uploader("Word-Datei (.docx) hochladen", type=["docx"])
    if word_file:
        try:
            from docx2pdf import convert
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(word_file.read())
                word_path = tmp.name
            output_path = word_path.replace(".docx", ".pdf")
            convert(word_path, output_path)
            with open(output_path, "rb") as f:
                st.download_button("📅 PDF herunterladen", data=f, file_name="converted.pdf")
        except Exception as e:
            st.error("❌ Konvertierung fehlgeschlagen – MS Word erforderlich.")
