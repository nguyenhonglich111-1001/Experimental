import pytest
import os
import PyPDF2
from nlp.tools.atomic_pdf_qa_streamlit.pdf_tool import PDFReaderTool, FilePathInputSchema



def test_pdf_reader_tool_success(dummy_pdf):
    """Test that the PDFReaderTool successfully reads a PDF and extracts content."""
    tool = PDFReaderTool()
    tool_input = FilePathInputSchema(file_path=dummy_pdf)
    result = tool.run(tool_input)
    assert result.text_content is not None
    assert isinstance(result.text_content, str)
    # For a blank PDF, extracted text should be empty or just whitespace
    assert result.text_content.strip() == ""

def test_pdf_reader_tool_file_not_found():
    """Test that the PDFReaderTool raises an error for a non-existent file."""
    tool = PDFReaderTool()
    non_existent_path = "non_existent_file.pdf"
    tool_input = FilePathInputSchema(file_path=non_existent_path)
    
    with pytest.raises(FileNotFoundError):
        tool.run(tool_input)
