from pydantic import BaseModel, Field
from typing import Type
from atomic_agents.lib.base.base_tool import BaseTool
import PyPDF2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FilePathInputSchema(BaseModel):
    """Input schema for the PDFReaderTool, requiring a file path."""
    file_path: str = Field(..., description="The absolute path to the PDF file.")

class PDFContentOutputSchema(BaseModel):
    """Output schema for the PDFReaderTool, providing the extracted text."""
    text_content: str = Field(..., description="The extracted text content from the PDF.")

class PDFReaderTool(BaseTool):
    name: str = "pdf_reader"
    description: str = "A tool to read and extract text content from a PDF file given its absolute path."
    input_schema: Type[BaseModel] = FilePathInputSchema
    output_schema: Type[BaseModel] = PDFContentOutputSchema

    def run(self, params: FilePathInputSchema) -> PDFContentOutputSchema:
        """Executes the tool with the provided parameters."""
        return self._run(params.file_path)

    def _run(self, file_path: str) -> PDFContentOutputSchema:
        """The internal method to run the tool's logic."""
        try:
            logging.info(f"Reading PDF file from path: {file_path}")
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            logging.info(f"Successfully extracted {len(text)} characters from PDF.")
            return PDFContentOutputSchema(text_content=text)
        except FileNotFoundError:
            logging.error(f"File not found at path: {file_path}")
            raise
        except Exception as e:
            logging.error(f"Error reading PDF file {file_path}: {e}")
            raise RuntimeError(f"Error reading PDF file {file_path}: {e}")

if __name__ == "__main__":
    # Example usage (for testing the tool independently)
    dummy_pdf_path = "dummy.pdf"
    try:
        writer = PyPDF2.PdfWriter()
        writer.add_blank_page(width=72, height=72)
        # Adding text to a PDF with PyPDF2 is complex; this dummy file will have no text.
        with open(dummy_pdf_path, "wb") as f:
            writer.write(f)

        tool = PDFReaderTool()
        tool_input = FilePathInputSchema(file_path=dummy_pdf_path)
        result = tool.run(tool_input)
        print(f"Extracted text length: {len(result.text_content)}")
        print(f"Extracted text (first 100 chars): '{result.text_content[:100]}'")
    except Exception as e:
        print(f"Tool execution failed: {e}")
    finally:
        import os
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
