import os
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, Type, AsyncGenerator

from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseAgentInputSchema, BaseAgentOutputSchema
from atomic_agents.lib.components.agent_memory import AgentMemory, Message
from atomic_agents.lib.base.base_tool import BaseTool # Corrected import path

# Import the PDFReaderTool we just created
from pdf_tool import PDFReaderTool, FilePathInputSchema, PDFContentOutputSchema

class BookQAAgentInputSchema(BaseAgentInputSchema):
    """Input schema for the BookQAAgent."""
    chat_message: str = Field(..., description="The user's question about the book.")
    pdf_file_path: Optional[str] = Field(None, description="The absolute path to the PDF file to analyze. Required for the first interaction or if a new book is uploaded.")

class BookQAAgentOutputSchema(BaseAgentOutputSchema):
    """Output schema for the BookQAAgent."""
    chat_message: str = Field(..., description="The agent's answer to the question based on the book content.")

class BookQAAgent(BaseAgent):
    input_schema: Type[BaseModel] = BookQAAgentInputSchema
    output_schema: Type[BaseModel] = BookQAAgentOutputSchema

    def __init__(self, config: BaseAgentConfig, pdf_content: Optional[str] = None):
        super().__init__(config)
        self.config = config
        self.pdf_content = pdf_content
        self.pdf_reader_tool = PDFReaderTool()
        self.current_pdf_path = None # Initialize current_pdf_path

    async def run(self, input_data: BookQAAgentInputSchema) -> AsyncGenerator[str, None]:
        # If a new PDF path is provided, read the content
        if input_data.pdf_file_path and (self.pdf_content is None or input_data.pdf_file_path != self.current_pdf_path):
            try:
                tool_input = FilePathInputSchema(file_path=input_data.pdf_file_path)
                pdf_read_result = self.pdf_reader_tool.run(tool_input)
                self.pdf_content = pdf_read_result.text_content
                self.current_pdf_path = input_data.pdf_file_path # Store current path to avoid re-reading
                # Add PDF content to agent's memory for context
                self.memory.add_message(role="system", content=self.output_schema(chat_message=f"The following is the content of the PDF book: {self.pdf_content}"))
                print(f"[DEBUG] PDF content loaded from {input_data.pdf_file_path}. Length: {len(self.pdf_content)}")
            except Exception as e:
                yield f"Error processing PDF: {e}"
                raise # Re-raise the exception after yielding the message
        
        if not self.pdf_content:
            yield "Please upload a PDF file first."
            return # Exit if no PDF content

        # Construct the prompt for the LLM, including PDF content and user's question
        # For large PDFs, this might exceed context window. A more advanced RAG would chunk and retrieve.
        # For this prototype, we'll pass the full content if it fits.
        # In a real RAG system, you'd use a vector store to retrieve relevant chunks.
        system_prompt_content = f"You are a helpful assistant that answers questions based on the provided book content. If the answer is not in the book, state that you don't know. The book content is: {self.pdf_content}"
        
        # Update system message in memory if it changes
        # Check if history is not empty and if the first message is a system message with different content
        if not self.memory.history or self.memory.history[0].role != "system" or self.memory.history[0].content.chat_message != system_prompt_content:
            # Clear existing system messages and add the new one to ensure it's always current
            new_history = [msg for msg in self.memory.history if msg.role != "system"]
            self.memory.history = [Message(role="system", content=self.output_schema(chat_message=system_prompt_content))] + new_history

        self.memory.add_message(role="user", content=self.input_schema(chat_message=input_data.chat_message, pdf_file_path=input_data.pdf_file_path))

        try:
            # Use the configured client from BaseAgentConfig
            messages = [{"role": msg.role, "content": msg.content.model_dump_json()} for msg in self.memory.history]
            response = await self.config.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
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
            self.memory.add_message(role="assistant", content=self.output_schema(chat_message=full_response_content))

        except Exception as e:
            print(f"[ERROR] LLM call failed: {e}")
            yield f"An error occurred while processing your request: {e}"
            raise # Re-raise the exception after yielding the message

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
        async for chunk in qa_agent.run(BookQAAgentInputSchema(chat_message="What is the main topic of this book?", pdf_file_path=dummy_pdf_path)):
            response_chunks.append(chunk)
        print(f"Agent: {''.join(response_chunks)}")

        # Subsequent interaction: ask another question without re-uploading
        print("\n--- Second Interaction (Asking another question) ---")
        response_chunks = []
        async for chunk in qa_agent.run(BookQAAgentInputSchema(chat_message="Can you tell me more about it?")):
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