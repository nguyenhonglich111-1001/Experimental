"""
A Streamlit application for processing and chatting with uploaded files using LangChain.
"""
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

# Define the path for the persistent Chroma database
PERSIST_DIRECTORY = "D:/LichNH/coding/Experimental/nlp/tools/langchain-file-processor/.chroma_db"

def get_google_api_key():
    """Fetches the Google API key from environment variables."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        # Fallback to OpenRouter API key if GOOGLE_API_KEY is not set
        google_api_key = os.getenv("OPENROUTER_API_KEY")
    return google_api_key

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Chat with your PDF", layout="wide")
    st.title("📄 Chat with Your PDF using LangChain")

    google_api_key = get_google_api_key()
    if not google_api_key:
        st.error("API key not found. Please set GOOGLE_API_KEY or OPENROUTER_API_KEY in your .env file.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)

    # Load existing vector store if it exists, otherwise initialize to None
    if "vector_store" not in st.session_state:
        if os.path.exists(PERSIST_DIRECTORY):
            st.session_state.vector_store = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        else:
            st.session_state.vector_store = None

    # File uploader
    uploaded_file = st.file_uploader("Upload your PDF file to create or update the vector store", type="pdf")

    if uploaded_file:
        try:
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write(f"Processing `{uploaded_file.name}`...")

            # 1. Load the document
            loader = PyPDFLoader(uploaded_file.name)
            documents = loader.load()

            # 2. Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
            texts = text_splitter.split_documents(documents)

            # 3. Create embeddings and vector store
            st.session_state.vector_store = Chroma.from_documents(
                texts, 
                embeddings, 
                persist_directory=PERSIST_DIRECTORY
            )

            st.success("File processed and vector store created/updated successfully! You can now ask questions.")

            # Clean up the temporary file
            os.remove(uploaded_file.name)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            if os.path.exists(uploaded_file.name):
                os.remove(uploaded_file.name)


    if st.session_state.vector_store:
        st.header("Ask a question about the document")
        user_question = st.text_input("Your question:")

        if user_question:
            try:
                # 4. Retrieve and generate answer
                llm = ChatGoogleGenerativeAI(
                    model="models/gemini-1.5-flash-latest", 
                    google_api_key=google_api_key, 
                    temperature=0.7,
                    convert_system_message_to_human=True
                )
                
                retriever = st.session_state.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
                
                # Use the RetrievalQA chain for a more integrated approach
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True
                )

                with st.spinner("Finding the answer..."):
                    response = qa_chain.invoke({"query": user_question})
                    st.write("### Answer")
                    st.write(response["result"])

                    with st.expander("Show source documents"):
                        st.write(response["source_documents"])

            except Exception as e:
                st.error(f"An error occurred while answering the question: {e}")


if __name__ == "__main__":
    main()
