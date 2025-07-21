import os
import streamlit as st
from langchain.chains import ConversationChain, RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import (ChatGoogleGenerativeAI,
                                    GoogleGenerativeAIEmbeddings)
from langchain.retrievers import ParentDocumentRetriever
from typing import List, Optional

from .langchain_logic import (classify_intent, delete_file, generate_sub_queries,
                               get_indexed_files, rerank_documents)

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


def display_chat_interface(
    llm: ChatGoogleGenerativeAI,
    retriever: Optional[ParentDocumentRetriever],
    vectorstore: Chroma,
    embeddings: GoogleGenerativeAIEmbeddings,
):
    """
    Handles the main chat interface, switching between direct LLM chat and RAG chat.
    """
    st.header("Chat with Gemini")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What would you like to ask?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = ""
            intent = classify_intent(llm, prompt)

            if intent == "list_files":
                files = get_indexed_files(vectorstore)
                if files:
                    response = "I have the following files in my knowledge base:"
                    st.markdown(response)
                    for file_path in files:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"- `{os.path.basename(file_path)}`")
                        with col2:
                            if st.button(f"Delete", key=f"delete_{file_path}"):
                                st.session_state.file_to_delete = file_path
                else:
                    response = "I do not have any files in my knowledge base yet. Please upload a PDF in the sidebar."
                    st.markdown(response)
            
            elif intent == "question_about_document" and retriever:
                response = handle_rag_query(prompt, llm, retriever, embeddings)
                st.markdown(response)

            else: # Handles "conversational" intent or questions when no doc is loaded
                response = handle_direct_llm_query(prompt, llm)
                st.markdown(response)
            
            if 'file_to_delete' in st.session_state and st.session_state.file_to_delete:
                file_path = st.session_state.file_to_delete
                st.warning(f"Are you sure you want to delete `{os.path.basename(file_path)}`? This action cannot be undone.")
                col1, col2, _ = st.columns([1, 1, 4])
                with col1:
                    if st.button("Yes, Delete", key=f"confirm_delete_{file_path}"):
                        if delete_file(vectorstore, file_path):
                            st.session_state.file_to_delete = None
                            st.experimental_rerun()
                        else:
                            # Error messages are handled within delete_file
                            st.session_state.file_to_delete = None
                with col2:
                    if st.button("Cancel", key=f"cancel_delete_{file_path}"):
                        st.session_state.file_to_delete = None
                        st.experimental_rerun()

        if response: # Avoid adding empty responses to history
            st.session_state.messages.append({"role": "assistant", "content": response})


def handle_direct_llm_query(prompt: str, llm: ChatGoogleGenerativeAI) -> str:
    """Handles a direct query to the LLM without retrieval."""
    with st.spinner("Thinking..."):
        conversation = ConversationChain(llm=llm, memory=ConversationBufferMemory())
        response = conversation.predict(input=prompt)
        return response


def handle_rag_query(
    prompt: str,
    llm: ChatGoogleGenerativeAI,
    retriever: ParentDocumentRetriever,
    embeddings: GoogleGenerativeAIEmbeddings,
) -> str:
    """Handles a query using the RAG workflow with query decomposition and citations."""
    with st.spinner("Breaking down question and searching document..."):
        sub_queries = generate_sub_queries(llm, prompt)
        
        with st.expander("Generated Sub-Queries"):
            st.write(sub_queries)

        all_retrieved_docs: List[Document] = []
        for q in sub_queries:
            all_retrieved_docs.extend(retriever.get_relevant_documents(q))
        
        unique_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())
        
        if not unique_docs:
            return "I couldn't find any relevant information in the document to answer your question. Please try rephrasing it."

        st.success(f"Retrieved {len(unique_docs)} unique document sections.")

    with st.spinner("Re-ranking retrieved documents for relevance..."):
        reranked_docs = rerank_documents(llm, prompt, unique_docs)
        top_docs = reranked_docs[:4] # Select top 4 documents
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
            
            # Display the sources with their citation numbers
            with st.expander("Cited Sources"):
                for i, doc in enumerate(response["source_documents"]):
                    st.markdown(f"**[source_{i+1}]** - *{os.path.basename(doc.metadata.get('source', 'N/A'))}*")
                    st.markdown(doc.page_content)
            
            return answer

        except Exception as e:
            st.error(f"An error occurred: {e}")
            return "An error occurred while processing the document."
