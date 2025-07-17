import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, Type

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.components.agent_memory import AgentMemory
from atomic_agents.lib.tools.base_tool import BaseTool

# Import the PDFReaderTool we just created
from .pdf_tool import PDFReaderTool, FilePathInputSchema, PDFContentOutputSchema

class BookQAAgentInputSchema(BaseAgentInputSchema):
    chat_message: str = Field(..., description="The user's question about the book.")
    pdf_file_path: Optional[str] = Field(None, description="The absolute path to the PDF file to analyze. Required for the first interaction or if a new book is uploaded.")

class BookQAAgentOutputSchema(BaseAgentOutputSchema):
    chat_message: str = Field(..., description="The agent's answer to the question based on the book content.")

class BookQAAgent(BaseAgent):
    def __init__(self, config: BaseAgentConfig, pdf_content: Optional[str] = None):
        super().__init__(config)
        self.pdf_content = pdf_content
        self.pdf_reader_tool = PDFReaderTool()

    @property
    def input_schema(self) -> Type[BaseModel]:
        return BookQAAgentInputSchema

    @property
    def output_schema(self) -> Type[BaseModel]:
        return BookQAAgentOutputSchema

    async def _run(self, input_data: BookQAAgentInputSchema) -> BookQAAgentOutputSchema:
        # If a new PDF path is provided, read the content
        if input_data.pdf_file_path and (self.pdf_content is None or input_data.pdf_file_path != self.current_pdf_path):
            try:
                pdf_read_result = self.pdf_reader_tool.run(file_path=input_data.pdf_file_path)
                self.pdf_content = pdf_read_result.text_content
                self.current_pdf_path = input_data.pdf_file_path # Store current path to avoid re-reading
                # Add PDF content to agent's memory for context
                self.memory.add_message("system", f"The following is the content of the PDF book: {self.pdf_content}")
                print(f"[DEBUG] PDF content loaded from {input_data.pdf_file_path}. Length: {len(self.pdf_content)}")
            except Exception as e:
                return BookQAAgentOutputSchema(chat_message=f"Error processing PDF: {e}")
        
        if not self.pdf_content:
            return BookQAAgentOutputSchema(chat_message="Please upload a PDF file first.")

        # Construct the prompt for the LLM, including PDF content and user's question
        # For large PDFs, this might exceed context window. A more advanced RAG would chunk and retrieve.
        # For this prototype, we'll pass the full content if it fits.
        # In a real RAG system, you'd use a vector store to retrieve relevant chunks.
        system_prompt_content = f"You are a helpful assistant that answers questions based on the provided book content. If the answer is not in the book, state that you don't know. The book content is: {self.pdf_content}"
        
        # Update system message in memory if it changes
        if not self.memory.history or self.memory.history[0].role != "system" or self.memory.history[0].content != system_prompt_content:
            self.memory.add_message("system", system_prompt_content)

        self.memory.add_message("user", input_data.chat_message)

        try:
            # Use the configured client from BaseAgentConfig
            response = await self.config.client.chat.completions.create(
                model=self.config.model,
                messages=self.memory.to_messages(),
                stream=True # Enable streaming for better UX in Streamlit
            )
            
            full_response_content = ""
            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    yield content_chunk
                    # Accumulate for memory after yielding
                    full_response_content += content_chunk
            
            # Add the full response to memory after streaming is complete
            self.memory.add_message("assistant", full_response_content)

        except Exception as e:
            print(f"[ERROR] LLM call failed: {e}")
            # For streaming, we might yield an error message or raise. For now, let's yield.
            yield f"An error occurred while processing your request: {e}"
            # Re-raise or handle appropriately if this is a critical error
            raise

# Example usage (for testing the agent independently)
async def main_test():
    # Setup OpenAI client (or Gemini via OpenAI-compatible API)
    # Ensure OPENAI_API_KEY or GEMINI_API_KEY is set in your environment
    # For Gemini, you might need to set base_url and model appropriately
    # client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    
    # Example for Gemini via OpenAI-compatible API
    client = instructor.from_openai(
        OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

    # Create a dummy PDF for testing
    dummy_pdf_path = "dummy_book.pdf"
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792) # Standard letter size
        writer.pages[0].add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        # Add some text content to the PDF (this is a simplified way, usually you'd use a library like reportlab or fpdf2)
        # For PyPDF2, adding text directly is complex. We'll just create a blank PDF.
        # Assume the PDFReaderTool will extract content from a real PDF.
        with open(dummy_pdf_path, "wb") as f:
            writer.write(f)
        print(f"Created dummy PDF at {dummy_pdf_path}")

        # Initialize agent config
        agent_config = BaseAgentConfig(
            client=client,
            model="gemini-2.0-flash-exp", # Use an appropriate Gemini model
            memory=AgentMemory()
        )

        # Initialize the agent
        qa_agent = BookQAAgent(config=agent_config)

        # First interaction: upload PDF and ask a question
        print("\n--- First Interaction (Uploading PDF) ---")
        # Collect streamed chunks
        response_chunks = []
        async for chunk in qa_agent._run(BookQAAgentInputSchema(chat_message="What is the main topic of this book?", pdf_file_path=dummy_pdf_path)):
            response_chunks.append(chunk)
        print(f"Agent: {''.join(response_chunks)}")

        # Subsequent interaction: ask another question without re-uploading
        print("\n--- Second Interaction (Asking another question) ---")
        response_chunks = []
        async for chunk in qa_agent._run(BookQAAgentInputSchema(chat_message="Can you tell me more about it?")):
            response_chunks.append(chunk)
        print(f"Agent: {''.join(response_chunks)}")

    except Exception as e:
        print(f"An error occurred during test: {e}")
    finally:
        import os
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
            print(f"Cleaned up dummy PDF at {dummy_pdf_path}")

if __name__ == "__main__":
    import asyncio
    # Ensure GEMINI_API_KEY is set in your environment or .env file
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main_test())

        except Exception as e:
            print(f"[ERROR] LLM call failed: {e}")
            return BookQAAgentOutputSchema(chat_message=f"An error occurred while processing your request: {e}")

# Example usage (for testing the agent independently)
async def main_test():
    # Setup OpenAI client (or Gemini via OpenAI-compatible API)
    # Ensure OPENAI_API_KEY or GEMINI_API_KEY is set in your environment
    # For Gemini, you might need to set base_url and model appropriately
    # client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
    
    # Example for Gemini via OpenAI-compatible API
    client = instructor.from_openai(
        OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    )

    # Create a dummy PDF for testing
    dummy_pdf_path = "dummy_book.pdf"
    try:
        from PyPDF2 import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792) # Standard letter size
        writer.pages[0].add_js("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        # Add some text content to the PDF (this is a simplified way, usually you'd use a library like reportlab or fpdf2)
        # For PyPDF2, adding text directly is complex. We'll just create a blank PDF.
        # Assume the PDFReaderTool will extract content from a real PDF.
        with open(dummy_pdf_path, "wb") as f:
            writer.write(f)
        print(f"Created dummy PDF at {dummy_pdf_path}")

        # Initialize agent config
        agent_config = BaseAgentConfig(
            client=client,
            model="gemini-2.0-flash-exp", # Use an appropriate Gemini model
            memory=AgentMemory()
        )

        # Initialize the agent
        qa_agent = BookQAAgent(config=agent_config)

        # First interaction: upload PDF and ask a question
        print("\n--- First Interaction (Uploading PDF) ---")
        response = await qa_agent._run(BookQAAgentInputSchema(chat_message="What is the main topic of this book?", pdf_file_path=dummy_pdf_path))
        print(f"Agent: {response.chat_message}")

        # Subsequent interaction: ask another question without re-uploading
        print("\n--- Second Interaction (Asking another question) ---")
        response = await qa_agent._run(BookQAAgentInputSchema(chat_message="Can you tell me more about it?"))
        print(f"Agent: {response.chat_message}")

    except Exception as e:
        print(f"An error occurred during test: {e}")
    finally:
        import os
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
            print(f"Cleaned up dummy PDF at {dummy_pdf_path}")

if __name__ == "__main__":
    import asyncio
    # Ensure GEMINI_API_KEY is set in your environment or .env file
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(main_test())