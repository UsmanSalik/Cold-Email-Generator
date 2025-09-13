# ingest.py
import os
import uuid
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create Chroma directory if it doesn't exist
CHROMA_DIR = "Chroma"
os.makedirs(CHROMA_DIR, exist_ok=True)

def create_user_vectorstore(portfolio_text, user_session_id, filename="portfolio.txt"):
    """Create a vectorstore for a specific user session from text."""
    try:
        # Create a unique directory for this user's vector store inside Chroma/
        user_vectorstore_path = os.path.join(CHROMA_DIR, f"chroma_db_{user_session_id}")
        os.makedirs("documents", exist_ok=True)
        
        # Save text to a temporary file
        temp_file_path = f"documents/{user_session_id}_{filename}"
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(portfolio_text)
        
        # Process the file
        success, message = create_vectorstore_from_file(temp_file_path, user_vectorstore_path)
        
        # Clean up the temporary file
        try:
            os.remove(temp_file_path)
        except:
            pass
            
        return success, message, user_vectorstore_path
        
    except Exception as e:
        return False, f"❌ Error saving portfolio: {str(e)}", None

def create_vectorstore_from_file(file_path, persist_directory=os.path.join(CHROMA_DIR, "chroma_db")):
    """Create vectorstore from uploaded file for a specific persist directory."""
    try:
        # Determine loader based on file extension
        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")
        
        # Load documents
        documents = loader.load()
        
        if not documents:
            return False, "❌ No content found in the file"
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create embeddings with optimized settings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={
                'batch_size': 32,
                'normalize_embeddings': False,
                'show_progress_bar': False
            }
        )
        
        # Create and persist vector store to the user-specific directory
        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        return True, f"✅ Portfolio processed successfully! ({len(chunks)} chunks created)"
        
    except Exception as e:
        return False, f"❌ Error processing file: {str(e)}"

def check_vectorstore_exists(vectorstore_path=os.path.join(CHROMA_DIR, "chroma_db")):
    """Check if a specific user's vectorstore exists and is not empty."""
    if not os.path.exists(vectorstore_path):
        return False
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        count = vectorstore._collection.count()
        return count > 0
    except:
        return False

def get_vectorstore_info(vectorstore_path=os.path.join(CHROMA_DIR, "chroma_db")):
    """Get information about a specific user's vectorstore."""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=embeddings
        )
        count = vectorstore._collection.count()
        return f"📊 Portfolio contains {count} knowledge chunks"
    except:
        return "📊 No portfolio data available"

def cleanup_user_vectorstore(vectorstore_path):
    """Clean up (delete) a user's vectorstore directory."""
    import shutil
    try:
        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
            return True
        return False
    except:
        return False

# Backward compatibility functions
def create_vectorstore_from_text(portfolio_text, filename="user_portfolio.txt"):
    """Legacy function for single-user mode"""
    return create_user_vectorstore(portfolio_text, "default_user", filename)