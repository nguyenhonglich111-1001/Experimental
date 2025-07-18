import pytest
import os
import PyPDF2

@pytest.fixture
def dummy_pdf(tmp_path):
    """Create a dummy PDF file for testing."""
    pdf_path = tmp_path / "dummy.pdf"
    writer = PyPDF2.PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with open(pdf_path, "wb") as f:
        writer.write(f)
    return str(pdf_path)
