import os
import fitz  # This is PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "./data"
DB_DIR = "./chroma_db"
COLLECTION_NAME = "nexla_documents"

def process_pdfs():
    print("1. Starting up the Database...")
    
    # Create a local database folder on your computer
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    
    # NEW: Use Chroma's default free local model! 
    # No API key needed. It runs entirely on your machine.
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    # Create a collection (like a table in a database) to hold our PDFs
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=default_ef
    )

    # Set up our "chopper" - 1000 letters per chunk
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    documents = []
    metadatas = []
    ids = []
    chunk_id_counter = 0

    print("2. Looking for PDFs...")
    
    # os.walk looks through your data folder AND all the numbered subfolders
    for root, dirs, files in os.walk(DATA_DIR):
        for filename in files:
            if not filename.endswith(".pdf"):
                continue # Skip anything that isn't a PDF
                
            file_path = os.path.join(root, filename)
            print(f"   -> Reading: {filename}")
            
            # Open the PDF
            doc = fitz.open(file_path)
            
            # Read page by page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if not text.strip():
                    continue # Skip empty pages
                    
                # Chop the page into chunks
                chunks = text_splitter.split_text(text)
                
                for chunk in chunks:
                    documents.append(chunk)
                    # Save exactly where this text came from!
                    metadatas.append({
                        "source": filename,
                        "page": page_num + 1 
                    })
                    ids.append(f"chunk_{chunk_id_counter}")
                    chunk_id_counter += 1
                    
            doc.close()

    if documents:
        print(f"3. Saving {len(documents)} text chunks into the database...")
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Done! Database is ready.")
    else:
        print("No text found. Did you put the PDFs in the data folder?")

if __name__ == "__main__":
    process_pdfs()