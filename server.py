from fastmcp import FastMCP
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize the MCP Server
mcp = FastMCP("Nexla_Document_Intelligence")

DB_DIR = "./chroma_db"
COLLECTION_NAME = "nexla_documents"

# 2. Connect to our existing local database and the free local AI model
chroma_client = chromadb.PersistentClient(path=DB_DIR)
default_ef = embedding_functions.DefaultEmbeddingFunction()
collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=default_ef)

# 3. Create the tool that AI agents will use
@mcp.tool()
def query_documents(question: str) -> str:
    """
    Search the Nexla PDF database to answer natural language questions.
    Returns the most relevant document sections, including source file and page numbers.
    """
    # Search the database for the top 5 most relevant chunks to the question
    results = collection.query(
        query_texts=[question],
        n_results=5
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "No relevant information found in the documents."
        
    # Format the results into a clean string for the AI to read
    formatted_answer = f"Found the following relevant context for the question: '{question}'\n\n"
    
    for i in range(len(results['documents'][0])):
        text_chunk = results['documents'][0][i]
        metadata = results['metadatas'][0][i]
        source_file = metadata.get('source', 'Unknown File')
        page_num = metadata.get('page', 'Unknown Page')
        
        # This fulfills the "Source Attribution" requirement!
        formatted_answer += f"--- Source: {source_file} (Page {page_num}) ---\n"
        formatted_answer += f"{text_chunk}\n\n"
        
    return formatted_answer

if __name__ == "__main__":
    # Starts the server and communicates via standard input/output
    mcp.run()