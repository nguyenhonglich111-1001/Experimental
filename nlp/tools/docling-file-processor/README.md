# Docling File Processor (Streamlit App)

This is a Streamlit-based web application that allows users to upload various document formats (PDF, DOCX, Images) and process them using the Docling library. The application extracts text and can perform OCR on image-based documents or scanned PDFs.

## Features

*   **File Upload:** Supports PDF, DOCX, PNG, JPG, JPEG file uploads.
*   **Docling Integration:** Utilizes the Docling library for robust document parsing.
*   **OCR Capability:** Integrates EasyOCR for text recognition in images and scanned PDFs.
*   **Text Extraction:** Displays the extracted text from processed documents.

## Setup and Running

1.  **Navigate to the directory:**
    ```bash
    cd nlp/tools/docling-file-processor
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Streamlit application:**
    ```bash
    streamlit run server.py
    ```

    The application will open in your web browser.

## Usage

1.  Open the application in your web browser.
2.  Use the "Choose a file" button to upload a document.
3.  Click "Process Document" to initiate Docling processing.
4.  View the extracted text in the "Extracted Text" section.

## Notes

*   For OCR functionality, `easyocr` will download necessary models on first run. This might take some time.
*   Ensure you have the necessary system dependencies for `easyocr` if you encounter issues (e.g., `Pillow`, `opencv-python`).
*   Uploaded files are temporarily stored in the `uploads/` directory and are removed after processing.
