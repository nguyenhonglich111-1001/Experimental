from pydantic import BaseModel, Field
from typing import Type
from atomic_agents.lib.base.base_tool import BaseTool
import PyPDF2

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

    def run(self, input_data: FilePathInputSchema) -> PDFContentOutputSchema:
        try:
            with open(input_data.file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() or ""
            return PDFContentOutputSchema(text_content=text)
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file {input_data.file_path}: {e}")

if __name__ == "__main__":
    # Example usage (for testing the tool independently)
    # Create a dummy PDF file for testing
    dummy_pdf_path = "dummy.pdf"
    writer = PyPDF2.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.pages[0].add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
    with open(dummy_pdf_path, "wb") as f:
        writer.write(f)

    tool = PDFReaderTool()
    try:
        tool_input = FilePathInputSchema(file_path=dummy_pdf_path)
        result = tool.run(tool_input)
        print(f"Extracted text length: {len(result.text_content)}")
        print(f"Extracted text (first 100 chars): {result.text_content[:100]}")
    except RuntimeError as e:
        print(f"Tool execution failed: {e}")
    finally:
        import os
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
