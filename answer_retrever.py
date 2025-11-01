# Filename: rag_form_autofill_optionC_refresh.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

from question_retrever import extract_questions_from_google_form  

# Load environment variables from .env file
load_dotenv()

# --- Global Configuration ---

API_KEY = os.getenv("GFF_key")
if not API_KEY:
    raise ValueError("API key not found. Please set GFF_key in your .env file.")
genai.configure(api_key=API_KEY)


# -------------------------------
# Load documents
# -------------------------------
def load_documents(file_paths):
    docs = []
    for path in file_paths:
        if not os.path.exists(path):
            print(f"Warning: File not found at {path}, skipping.")
            continue
        if path.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif path.endswith(".docx"):
            loader = Docx2txtLoader(path)
        else:  # txt fallback
            loader = TextLoader(path)
        docs.extend(loader.load())
    return docs

# -------------------------------
# Create vector store (MODIFIED SECTION)
# -------------------------------
def create_vector_store(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(docs)

    print("Initializing local embedding model (downloading if this is the first time)...")
    embeddings = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-base" # A good, general-purpose model
    )
    
    print("Creating vector store from documents...")
    vector_store = FAISS.from_documents(split_docs, embeddings)
    print("Vector store created successfully.")
    return vector_store

# -------------------------------
# Generate answers using RAG with fallback + periodic context refresh
# -------------------------------
def generate_answers_rag_with_refresh(form_data, vector_store, top_k=3, context_refresh_interval=5):
    """
    form_data: list of dicts with 'question' and 'options'
    vector_store: FAISS vector store with context embeddings
    top_k: number of top relevant chunks to retrieve
    context_refresh_interval: refresh context after every n questions
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    
    answered = []
    last_context_text = ""
    
    for i, q in enumerate(form_data, start=1):
        question_text = q.get("question", "")
        options = q.get("options", [])
        options_str = "\n".join([f"- {opt}" for opt in options]) if options else "None"
        
        # Retrieve relevant context
        # relevant_docs = retriever.get_relevant_documents(question_text)
        relevant_docs = retriever.invoke(question_text)
        
        if relevant_docs:
            context_text = "\n\n".join([doc.page_content for doc in relevant_docs])
            source = "from context"
        else:
            context_text = ""
            source = "general knowledge"
        
        # Periodic context refresh: every N questions, resend last context
        if i % context_refresh_interval == 0 and last_context_text:
            context_text = last_context_text  # refresh previous context
        
        # Save last non-empty context
        if context_text:
            last_context_text = context_text
        
        prompt = f"""
You are an intelligent assistant filling a Google Form.

Question: {question_text}
Options (if any):
{options_str}

{"Use the following context to answer the question:\n" + context_text if context_text else "No relevant context found."}

Generate only the final answer (no explanation).
"""
        
        # Use the configured model to generate content
        response = model.generate_content(prompt)
        
        answer_text = response.text.strip() if response and response.text else "No answer generated"
        q["answer"] = answer_text
        q["answer_source"] = source
        answered.append(q)
    
    return answered

# -------------------------------
# Full pipeline
# -------------------------------
def rag_pipeline_with_refresh(form_url, doc_paths, top_k=3, context_refresh_interval=5):
    # Step 1: Extract questions
    questions = extract_questions_from_google_form(form_url)
    
    # Step 2: Load documents and create vector store
    docs = load_documents(doc_paths)
    vector_store = create_vector_store(docs)
    
    # Step 3: Generate answers with periodic context refresh
    filled_form = generate_answers_rag_with_refresh(
        questions, vector_store,
        top_k=top_k,
        context_refresh_interval=context_refresh_interval
    )
    return filled_form

# -------------------------------
# Example usage
# -------------------------------
# if __name__ == "__main__":
#     FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScP8ZvKzWqo496iHhBYp99ygcSEGADD4LOJAaXjspkYvfRBnw/viewform?usp=header"
#     DOCUMENTS = [r"test_files\GFF_sample_context_text_file_2.pdf", r"test_files\GFF_sample_context_text_file.docx"]  # Add your files

#     filled_form = rag_pipeline_with_refresh(
#         FORM_URL, DOCUMENTS,
#         top_k=3,
#         context_refresh_interval=5  # Refresh context every 5 questions
#     )
    
#     print("\n--- Final Answers ---")
#     for q in filled_form:
#         print(f"Q: {q['question']}")
#         print(f"A: {q['answer']} (Source: {q['answer_source']})")
#         print("-" * 60)