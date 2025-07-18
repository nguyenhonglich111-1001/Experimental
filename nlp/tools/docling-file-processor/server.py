import streamlit as st
import os
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
import tempfile

# Load environment variables (if any)
load_dotenv()

# --- Configuration ---
UPLOAD_DIR = "nlp/tools/docling-file-processor/uploads"
# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Streamlit UI ---
st.set_page_config(page_title="Docling File Processor", layout="centered")
st.title("📄 Docling File Processor")
st.markdown("Upload a document (PDF, DOCX, Image) to process it with Docling.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded content
    with tempfile.NamedTemporaryFile(delete=False, dir=UPLOAD_DIR, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        filepath = tmp_file.name
    
    st.info(f"File saved temporarily at: {filepath}")

    if st.button("Process Document"):
        st.subheader("Processing Results:")
        
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        input_format = None
        format_option = None

        if file_extension == '.pdf':
            input_format = InputFormat.PDF
            # Enable OCR for PDFs by default
            pipeline_options = PdfPipelineOptions(ocr_options=EasyOcrOptions(lang=['en']))
            format_option = PdfFormatOption(pipeline_options=pipeline_options)
            st.info("Processing PDF with OCR (EasyOCR, English language).")
        elif file_extension in ['.png', '.jpg', '.jpeg']:
            input_format = InputFormat.IMAGE
            format_option = ImageFormatOption() # Default image options
            st.info("Processing Image file.")
        elif file_extension == '.docx':
            input_format = InputFormat.DOCX
            # Docling might need specific backend/pipeline for DOCX, using default for now
            format_option = None # Docling will use default for DOCX if not specified
            st.info("Processing DOCX file.")
        else:
            st.error(f"Unsupported file format: {file_extension}")
            # Clean up the temporary file
            os.remove(filepath)
            st.stop()

        if input_format:
            converter = DocumentConverter()
            try:
                with st.spinner("Docling is processing your document... This might take a moment."):
                    result = converter.convert(filepath, input_format, format_option=format_option)

                if result.status == "SUCCESS":
                    st.success("Document processed successfully!")
                    
                    # Display extracted text
                    st.markdown("### Extracted Text:")
                    processed_text = result.document.export_to_text()
                    if processed_text:
                        st.text_area("Full Text", processed_text, height=300)
                    else:
                        st.warning("No text extracted from the document.")
                    
                    # You can add more result displays here, e.g., for tables, images, etc.
                    # For example, to visualize the document (requires PIL/Pillow and potentially other dependencies for rendering)
                    # try:
                    #     st.markdown("### Document Visualization:")
                    #     visualization_images = result.document.get_visualization()
                    #     for page_no, img in visualization_images.items():
                    #         st.image(img, caption=f"Page {page_no}", use_column_width=True)
                    # except Exception as viz_e:
                    #     st.warning(f"Could not generate document visualization: {viz_e}")

                elif result.status == "PARTIAL_SUCCESS":
                    st.warning("Document processed with partial success. Some errors occurred.")
                    st.error(f"Errors: {result.errors}")
                    st.text_area("Partial Text", result.document.export_to_text(), height=200)
                else:
                    st.error(f"Docling processing failed: {result.status}")
                    if result.errors:
                        st.error(f"Details: {result.errors}")

            except Exception as e:
                st.error(f"An unexpected error occurred during Docling processing: {e}")
        
        # Clean up the temporary file after processing
        if os.path.exists(filepath):
            os.remove(filepath)
            st.success(f"Temporary file removed: {os.path.basename(filepath)}")
