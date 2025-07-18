import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, Type, AsyncGenerator
import logging

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.base.base_tool import BaseTool

from nlp.tools.atomic_pdf_qa_streamlit.pdf_tool import PDFReaderTool, FilePathInputSchema

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BookQAAgentInputSchema(BaseAgentInputSchema):
    """Input schema for the BookQAAgent."""
    chat_message: str = Field(..., description="The user's question about the book.")
    pdf_file_path: Optional[str] = Field(None, description="The absolute path to the PDF file to analyze. Required for the first interaction or if a new book is uploaded.")

class BookQAAgentOutputSchema(BaseAgentOutputSchema):
    """Output schema for the BookQAAgent."""
    chat_message: str = Field(..., description="The agent's answer to the question based on the book content.")

class BookQAAgent(BaseAgent):
    def __init__(self, config: BaseAgentConfig):
        super().__init__(config=config)
        self.pdf_content: Optional[str] = None
        self.current_pdf_path: Optional[str] = None
        self.pdf_reader_tool = PDFReaderTool()

    async def _run(self, input_data: BookQAAgentInputSchema) -> AsyncGenerator[str, None]:
        if input_data.pdf_file_path and input_data.pdf_file_path != self.current_pdf_path:
            try:
                logging.info(f"Processing new PDF: {input_data.pdf_file_path}")
                tool_input = FilePathInputSchema(file_path=input_data.pdf_file_path)
                pdf_read_result = self.pdf_reader_tool.run(tool_input)
                self.pdf_content = pdf_read_result.text_content
                self.current_pdf_path = input_data.pdf_file_path
                
                system_prompt_content = f"You are a helpful assistant. Answer questions based on the provided book content. If the answer isn't in the book, say so. Book content: {self.pdf_content}"
                self.memory.reset() # Clear memory for the new book
                self.memory.add_message("system", self.output_schema(chat_message=system_prompt_content))
                logging.info(f"PDF content loaded. Length: {len(self.pdf_content)}")
            except Exception as e:
                error_message = f"Error processing PDF: {e}"
                logging.error(error_message)
                yield error_message
                return

        if not self.pdf_content:
            yield "Please upload a PDF file first."
            return

        self.memory.add_message("user", input_data)

        try:
            response = await self.config.client.chat.completions.create(
                model=self.config.model,
                messages=self.memory.to_messages(),
                stream=True
            )
            
            full_response_content = ""
            async for chunk in response:
                content_chunk = chunk.choices[0].delta.content or ""
                yield content_chunk
                full_response_content += content_chunk
            
            self.memory.add_message("assistant", self.output_schema(chat_message=full_response_content))

        except Exception as e:
            error_message = f"LLM call failed: {e}"
            logging.error(error_message)
            yield f"An error occurred: {e}"

# Example usage for independent testing
async def main_test():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables.")
        return

    client = instructor.from_openai(
        OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    )

    dummy_pdf_path = "dummy_book.pdf"
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with open(dummy_pdf_path, "wb") as f:
            writer.write(f)
        print(f"Created dummy PDF at {dummy_pdf_path}")

        agent_config = BaseAgentConfig(
            client=client,
            model="gemini-2.0-flash-exp",
            memory=AgentMemory()
        )
        qa_agent = BookQAAgent(config=agent_config)

        print("\n--- First Interaction ---")
        input_data1 = BookQAAgentInputSchema(chat_message="What is this book about?", pdf_file_path=dummy_pdf_path)
        response_chunks = [chunk async for chunk in qa_agent.run_async(input_data1)]
        print(f"Agent: {''.join(response_chunks)}")

        print("\n--- Second Interaction ---")
        input_data2 = BookQAAgentInputSchema(chat_message="Can you elaborate?")
        response_chunks = [chunk async for chunk in qa_agent.run_async(input_data2)]
        print(f"Agent: {''.join(response_chunks)}")

    except Exception as e:
        print(f"An error occurred during test: {e}")
    finally:
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
            print(f"Cleaned up dummy PDF at {dummy_pdf_path}")

if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    asyncio.run(main_test())