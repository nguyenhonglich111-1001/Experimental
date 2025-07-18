import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from pydantic import BaseModel
from typing import AsyncGenerator
import instructor

from nlp.tools.atomic_pdf_qa_streamlit.book_qa_agent import BookQAAgent, BookQAAgentInputSchema
from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.agent_memory import AgentMemory

# Mock the instructor/OpenAI client
class MockChoiceDelta(BaseModel):
    content: str

class MockChoice(BaseModel):
    delta: MockChoiceDelta

class MockStreamChunk(BaseModel):
    choices: list[MockChoice]

async def mock_streaming_response():
    response_chunks = ["This ", "is ", "a ", "mocked ", "response."]
    for chunk in response_chunks:
        yield MockStreamChunk(choices=[MockChoice(delta=MockChoiceDelta(content=chunk))])

@pytest.fixture
def mock_llm_client():
    """Fixture to create a mock LLM client that behaves like an Instructor instance."""
    mock_instructor = MagicMock(spec=instructor.Instructor)
    async def mock_create_side_effect(*args, **kwargs):
        async for chunk in mock_streaming_response():
            yield chunk
    mock_instructor.chat.completions.create = AsyncMock(side_effect=mock_create_side_effect)
    return mock_instructor

@pytest.fixture
def agent_config(mock_llm_client):
    """Fixture to create a BaseAgentConfig with the mock client."""
    return BaseAgentConfig(
        client=mock_llm_client,
        model="mock-model",
        memory=AgentMemory()
    )

@pytest_asyncio.fixture
async def qa_agent(agent_config):
    """Fixture to create an instance of the BookQAAgent."""
    return BookQAAgent(config=agent_config)

@pytest.mark.asyncio
async def test_agent_no_pdf_error(qa_agent: BookQAAgent):
    """Test that the agent returns an error if no PDF is provided."""
    input_data = BookQAAgentInputSchema(chat_message="What is this book about?")
    response_generator = qa_agent.run_async(input_data)
    
    chunks = [chunk async for chunk in response_generator]
    full_response = "".join(chunks)
    
    assert "Please upload a PDF file first." in full_response

@pytest.mark.asyncio
async def test_agent_pdf_loading_and_qna(qa_agent: BookQAAgent, dummy_pdf):
    """Test the full flow: loading a PDF, asking a question, and getting a mocked response."""
    # 1. First interaction: Load PDF and ask a question
    input_data1 = BookQAAgentInputSchema(
        chat_message="What is this book about?",
        pdf_file_path=dummy_pdf
    )
    
    response_generator1 = qa_agent.run_async(input_data1)
    chunks1 = [chunk async for chunk in response_generator1]
    full_response1 = "".join(chunks1)
    
    # Assertions for the first interaction
    assert qa_agent.pdf_content is not None
    assert qa_agent.current_pdf_path == dummy_pdf
    assert "This is a mocked response." in full_response1
    
    # Check memory after first interaction
    assert len(qa_agent.memory.history) == 3 # System, User, Assistant
    assert qa_agent.memory.history[0].role == "system"
    assert "The following is the content of the PDF book" in qa_agent.memory.history[0].content.chat_message
    assert qa_agent.memory.history[1].role == "user"
    assert qa_agent.memory.history[1].content.chat_message == "What is this book about?"
    assert qa_agent.memory.history[2].role == "assistant"
    assert qa_agent.memory.history[2].content.chat_message == "This is a mocked response."
    
    # 2. Second interaction: Ask another question (without providing PDF path)
    # Re-mock the client's create method for the second call
    qa_agent.config.client.chat.completions.create = AsyncMock(return_value=mock_streaming_response())
    
    input_data2 = BookQAAgentInputSchema(chat_message="Tell me more.")
    
    response_generator2 = qa_agent.run_async(input_data2)
    chunks2 = [chunk async for chunk in response_generator2]
    full_response2 = "".join(chunks2)
    
    # Assertions for the second interaction
    assert "This is a mocked response." in full_response2
    
    # Check memory after second interaction
    assert len(qa_agent.memory.history) == 5 # System, User, Assistant, User, Assistant
    assert qa_agent.memory.history[3].role == "user"
    assert qa_agent.memory.history[3].content.chat_message == "Tell me more."
    assert qa_agent.memory.history[4].role == "assistant"
    assert qa_agent.memory.history[4].content.chat_message == "This is a mocked response."
