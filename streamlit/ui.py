import os
import time
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from app.controllers.file_process_controller import FileProcessController

st.set_page_config(page_title="PDF Processor", layout="centered")

st.title("Upload PDF → Processing progress")

@st.cache_resource
def get_executor():
    return ThreadPoolExecutor(max_workers=1)

executor = get_executor()

if "future" not in st.session_state:
    st.session_state.future = None
if "tmp_pdf_path" not in st.session_state:
    st.session_state.tmp_pdf_path = None
if "started_at" not in st.session_state:
    st.session_state.started_at = None
if "done" not in st.session_state:
    st.session_state.done = False
if "error" not in st.session_state:
    st.session_state.error = None


def start_processing(pdf_bytes: bytes, original_name: str):
    tmp_dir = tempfile.mkdtemp(prefix="pdf_upload_")
    safe_name = Path(original_name).name or "uploaded.pdf"
    pdf_path = os.path.join(tmp_dir, safe_name)

    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)

    st.session_state.tmp_pdf_path = pdf_path
    st.session_state.started_at = time.time()
    st.session_state.done = False
    st.session_state.error = None

    def job():
        controller = FileProcessController(pdf_path=pdf_path)
        controller.process()

    st.session_state.future = executor.submit(job)


uploaded = st.file_uploader("Carica un PDF", type=["pdf"])

col1, col2 = st.columns([1, 1])
with col1:
    start_btn = st.button(
        "Avvia processing",
        disabled=(uploaded is None) or (st.session_state.future is not None and not st.session_state.future.done()),
        use_container_width=True,
    )

with col2:
    reset_btn = st.button("Reset", use_container_width=True)

if reset_btn:
    st.session_state.future = None
    st.session_state.tmp_pdf_path = None
    st.session_state.started_at = None
    st.session_state.done = False
    st.session_state.error = None
    st.rerun()

if start_btn and uploaded is not None:
    start_processing(uploaded.getvalue(), uploaded.name)
    st.rerun()

if st.session_state.future is not None:
    st.subheader("Stato elaborazione")

    progress_bar = st.progress(0)
    status = st.empty()


    MAX_FAKE = 95
    SPEED_SECONDS_TO_MAX = 30

    try:
        while True:
            future = st.session_state.future

            if future.done():
                exc = future.exception()
                if exc:
                    st.session_state.error = str(exc)
                    status.error(f"Errore durante il processing: {st.session_state.error}")
                    progress_bar.progress(0)
                else:
                    progress_bar.progress(100)
                    status.success("Processing completato ✅")
                    st.session_state.done = True
                break

            elapsed = max(0.0, time.time() - (st.session_state.started_at or time.time()))
            fake_pct = min(MAX_FAKE, int((elapsed / SPEED_SECONDS_TO_MAX) * MAX_FAKE))
            progress_bar.progress(fake_pct)
            status.info(f"Processing in corso… {fake_pct}%")

            time.sleep(0.25)

    except Exception as e:
        status.error(f"Errore UI: {e}")

    if st.session_state.tmp_pdf_path:
        st.caption(f"File temporaneo: {st.session_state.tmp_pdf_path}")

else:
    st.info("Carica un PDF e premi **Avvia processing**.")
