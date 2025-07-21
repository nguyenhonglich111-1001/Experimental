from typing import List, Tuple
import os
import re
import chromadb
import streamlit as st
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)
from typing import List, Optional

from .config import (CHILD_CHUNK_SIZE, EMBEDDINGS_MODEL, LLM_MODEL,
                    PARENT_CHUNK_SIZE, PERSIST_DIRECTORY)

@st.cache_resource
def get_llm(api_key: str) -> ChatGoogleGenerativeAI:
    """Initializes and caches the LLM."""
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=api_key,
        temperature=0.7,
    )

@st.cache_resource
def get_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Initializes and caches the embeddings model."""
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDINGS_MODEL, google_api_key=api_key
    )

def build_vector_store(
    embeddings: GoogleGenerativeAIEmbeddings,
) -> Chroma:
    """Builds and caches the Chroma vector store."""
    return Chroma(
        collection_name="split_parents",
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIRECTORY),
        client_settings=chromadb.Settings(allow_reset=True),
    )

def build_retriever(
    vectorstore: Chroma, docs: List[Document]
) -> ParentDocumentRetriever:
    """Builds the ParentDocumentRetriever and adds documents to it."""
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=PARENT_CHUNK_SIZE)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=CHILD_CHUNK_SIZE)
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    
    retriever.add_documents(docs, ids=None)
    return retriever

def get_indexed_files(vectorstore: Chroma) -> List[str]:
    """Retrieves the list of unique source file names from the vector store."""
    if not vectorstore:
        return []
    
    try:
        all_docs = vectorstore.get()
        if not all_docs or not all_docs.get("metadatas"):
            return []
        
        unique_sources = set()
        for metadata in all_docs["metadatas"]:
            if "source" in metadata:
                unique_sources.add(metadata["source"])
        
        return list(unique_sources)
    except Exception:
        # This can happen if the collection doesn't exist yet
        return []

@st.cache_data
def classify_intent(_llm: ChatGoogleGenerativeAI, query: str) -> str:
    """Uses an LLM to classify the user's intent."""
    system_message = """
    You are an intent classifier. Your job is to determine the user's intent based on their message.
    There are three possible intents:
    1. "conversational": For greetings, farewells, thank yous, or other general chat.
    2. "list_files": For when the user explicitly asks to see the list of loaded files.
    3. "question_about_document": For any question that should be answered from the loaded document.

    Respond with ONLY one of the three intent names.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{question}"),
        ]
    )
    
    chain = prompt | _llm | StrOutputParser()
    result = chain.invoke({"question": query})
    return result.strip()

@st.cache_data
def generate_sub_queries(_llm: ChatGoogleGenerativeAI, query: str, chat_history: List[dict]) -> List[str]:
    """
    Uses an LLM to break down a complex or conversational query into simpler, self-contained sub-queries.
    """
    # Format the chat history into a string
    history_str = ""
    for message in chat_history:
        if message["role"] == "user":
            history_str += f"Human: {message['content']}\n"
        elif message["role"] == "assistant":
            history_str += f"AI: {message['content']}\n"

    system_message = f"""
    You are an expert at query rewriting and decomposition. Your goal is to reformulate the user's latest question into a set of simple, self-contained sub-queries that a semantic search system can effectively answer.

    Use the provided conversation history to understand the full context of the user's request.
    Resolve pronouns (e.g., "it", "that", "they") and ambiguous references based on the preceding conversation.
    The rewritten queries must be explicit and stand on their own.

    - For broad requests (e.g., "list all...", "summarize..."), first generate a query to find the general context, then generate queries to extract the specific details.
    - Each sub-query should be on a new line.
    - Do not number the sub-queries.

    Conversation History:
    {history_str}
    """
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{question}"),
        ]
    )
    
    chain = prompt | _llm | StrOutputParser()
    result = chain.invoke({"question": query})
    return [q.strip() for q in result.split("\n") if q.strip()]

@st.cache_data
def extract_chapter_from_query(_llm: ChatGoogleGenerativeAI, query: str) -> Optional[int]:
    """
    Uses an LLM to extract a chapter number from a user query.
    """
    system_message = """
    You are an expert at extracting specific information. Your only job is to find a chapter number in the user's query.
    
    - If you find a chapter number, respond with ONLY the integer number (e.g., "4", "12").
    - If you do not find any reference to a chapter, respond with the word "None".
    - Do not add any explanation or conversational text.
    """
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{question}"),
        ]
    )
    
    chain = prompt | _llm | StrOutputParser()
    result = chain.invoke({"question": query}).strip()
    
    # Find the first number in the LLM's response
    match = re.search(r'\d+', result)
    if match:
        return int(match.group(0))
    return None

def rerank_documents(
    _llm: ChatGoogleGenerativeAI, query: str, documents: List[Document]
) -> List[Document]:
    """Uses an LLM to re-rank a list of documents based on their relevance to the query."""
    if not documents:
        return []

    prompt = ChatPromptTemplate.from_template(
        """
    You are a document re-ranking expert.
    Given a query and a list of documents, your task is to assign a relevance score to each document.
    The score should be an integer between 1 and 10, where 10 is the most relevant.

    Respond with a list of scores, one for each document, in the same order.
    The output should be a comma-separated string of numbers, e.g., "8,5,9,3".

    Query: {query}

    Documents:
    {docs}
    """
    )

    chain = prompt | _llm | StrOutputParser()

    doc_strings = [
        f"ID: {i}\nContent: {doc.page_content}"
        for i, doc in enumerate(documents)
    ]
    
    result = chain.invoke({"query": query, "docs": "\n---\n".join(doc_strings)})
    
    try:
        scores = [float(s.strip()) for s in result.split(",")]
        
        if len(scores) != len(documents):
            st.error("Re-ranking returned a different number of scores than documents.")
            return documents

        scored_docs = sorted(
            zip(scores, documents), key=lambda x: x[0], reverse=True
        )
        
        return [doc for score, doc in scored_docs]

    except ValueError:
        st.error(f"Error parsing re-ranking scores: {result}")
        return documents

def delete_file(vectorstore: Chroma, file_path: str) -> bool:
    """
    Deletes a file and its corresponding entries from the vector store.
    """
    if not file_path or not os.path.exists(file_path):
        st.error(f"File not found: {file_path}")
        return False

    all_docs = vectorstore.get(where={"source": file_path})
    doc_ids = all_docs.get("ids", [])

    if doc_ids:
        vectorstore.delete(ids=doc_ids)
        st.success(f"Removed {len(doc_ids)} document chunks from the vector store.")
    else:
        st.warning(f"No documents found in vector store for: {os.path.basename(file_path)}")

    os.remove(file_path)
    st.success(f"Successfully deleted file: {os.path.basename(file_path)}")
    
    return True

# --- Prompt Templates ---

CITATION_PROMPT = PromptTemplate(
    template="""You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Your answer should be comprehensive and directly based on the provided context.

After each sentence or claim in your answer, you MUST cite the source document it came from.
To cite, use the format [source_N] where N is the number of the source document.
For example:
'The sky is blue [source_1]. The grass is green [source_2].'

Context:
{context}

Question: {question}
Answer with Citations:""",
    input_variables=["context", "question"],
)

def handle_direct_llm_query(prompt: str, llm: ChatGoogleGenerativeAI) -> str:
    """Handles a direct query to the LLM without retrieval, maintaining conversation history."""
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt_template | llm | StrOutputParser()

    conversational_chain = RunnableWithMessageHistory(
        chain,
        lambda session_id: StreamlitChatMessageHistory(key="messages"),
        input_messages_key="input",
        history_messages_key="history",
    )
    
    with st.spinner("Thinking..."):
        response = conversational_chain.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": "any"}},
        )
        return response


def handle_rag_query(
    prompt: str,
    llm: ChatGoogleGenerativeAI,
    retriever: ParentDocumentRetriever,
    embeddings: GoogleGenerativeAIEmbeddings,
    chat_history: List[dict],
) -> str:
    """Handles a query using the RAG workflow with query decomposition and citations."""
    with st.spinner("Analyzing conversation and breaking down question..."):
        sub_queries = generate_sub_queries(llm, prompt, chat_history)
        
        with st.expander("Generated Sub-Queries"):
            st.write(sub_queries)

        all_retrieved_docs: List[Document] = []
        for q in sub_queries:
            chapter_num = extract_chapter_from_query(llm, q)
            
            search_kwargs = {}
            if chapter_num is not None:
                st.info(f"Filtering search to Chapter {chapter_num}...")
                search_kwargs = {"filter": {"chapter": chapter_num}}

            retrieved = retriever.get_relevant_documents(q, search_kwargs=search_kwargs)
            all_retrieved_docs.extend(retrieved)
        
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())
        
        if not unique_docs:
            return "I couldn't find any relevant information in the document to answer your question."

        st.success(f"Retrieved {len(unique_docs)} unique document sections.")

    with st.spinner("Re-ranking retrieved documents for relevance..."):
        reranked_docs = rerank_documents(llm, prompt, unique_docs)
        top_docs = reranked_docs[:4]
        st.success(f"Re-ranked and selected top {len(top_docs)} documents.")

    with st.spinner("Synthesizing the final answer with citations..."):
        try:
            contextual_vectorstore = Chroma.from_documents(top_docs, embeddings)

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=contextual_vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": CITATION_PROMPT},
                return_source_documents=True,
            )

            response = qa_chain.invoke({"query": prompt})
            answer = response.get("result", "Sorry, I couldn't find an answer.")
            
            with st.expander("Cited Sources"):
                for i, doc in enumerate(response["source_documents"]):
                    st.markdown(f"**[source_{i+1}]** - *{os.path.basename(doc.metadata.get('source', 'N/A'))}*")
                    st.markdown(doc.page_content)
            
            return answer

        except Exception as e:
            st.error(f"An error occurred: {e}")
            return "An error occurred while processing the document."
