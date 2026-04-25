This repository contains a fully local, privacy-first Model Context Protocol (MCP) server designed to expose unstructured PDF document intelligence to AI agents.

## 🏗️ Architecture & Technology Choices
I optimized for a **100% local, zero-dependency** stack to ensure the reviewer can clone and run this without needing external API keys, Docker containers, or cloud database provisioning. 

* **Framework:** `FastMCP` (Anthropic SDK) - Chosen for rapid, clean tool exposure and standard `stdio` compliance.
* **PDF Parsing:** `PyMuPDF` (`fitz`) - Extremely fast, handles complex layouts, and easily extracts strict page-level metadata.
* **Vector Store:** `ChromaDB` - Runs entirely locally (SQLite-backed). No external daemon required.
* **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`) - A free, local embedding model that completely removes the need for OpenAI/Anthropic API keys, ensuring maximum data privacy.

### Trade-offs Considered
* **Local Embeddings vs. Cloud APIs:** By using a local sentence-transformer, ingestion relies on the CPU. While this takes longer for massive datasets (e.g., 60,000+ chunks), it is ideal for this prototype scope (5 PDFs) and guarantees that highly sensitive enterprise documents never leave the local network. 
* **Chunking Strategy:** I used a standard 1000-character chunk with a 200-character overlap. For a true production system, I would upgrade to semantic chunking or layout-aware chunking (e.g., keeping tables intact), but character-splitting is robust enough for this baseline Q&A tool.

## 🚀 Setup & Execution Instructions

**1. Environment Setup**
Ensure you have Python 3.10+ installed.
```bash
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

2. Install Dependencies
    pip install -r requirements.txt
    (Note: ChromaDB currently requires numpy<2.0.0 due to deprecations in the recent Numpy 2.0 release, which is strictly defined in the requirements file).

3. Data Ingestion
    Place your 5 test PDFs into the ./data directory, then run the ingestion script:
    python ingest.py

    This will parse the PDFs, generate embeddings locally, and save them to a local ./chroma_db directory.

4. Run the Server (Testing)
    You can interact with the server using the official MCP Inspector:
    npx @modelcontextprotocol/inspector python server.py

🛠️ Expose Tools
    query_documents
        Description: Searches the Nexla PDF database to answer natural language questions.

        Input Schema: {"question": "string"}

        Output: Returns the top 5 most semantically relevant text chunks, formatted with strict source file and page number attribution.

🤖 Vibe Coding & AI Tooling Reflection
    For this assignment, I utilized an AI assistant (Google Gemini) as an interactive pair-programmer.

    How I used it:

    I used the AI to rapidly generate boilerplate for FastMCP and the ChromaDB ingestion pipeline, allowing me to focus on the architectural logic rather than syntax.
    I leaned on the AI to help debug runtime environment issues.

Challenges & Corrections:
    Dependency Hell: During setup, the initial environment crashed due to the numpy 2.0 update breaking ChromaDB's reliance on np.float_. The AI helped identify the root cause quickly, allowing us to pin numpy<2.0.0 and move forward.

    Scope Creep: Initially, my data folder contained over 100 PDFs. Because I chose a local embedding model, the AI correctly pointed out that processing 60,000+ chunks purely on CPU would blow past the 3-4 hour time limit. I stepped in, aborted the process, wiped the half-built database, and strictly limited the input to the 5 requested PDFs, reducing ingestion time to under a minute.

    View on AI in Software Engineering:
    AI tooling is essentially a "technical co-founder" that operates at the speed of thought. It is incredible for scaffolding and debugging, but it lacks situational awareness. The engineer's primary job has shifted from writing every line of code to managing architectural boundaries, making conscious trade-offs (like deciding when a local CPU model is "good enough" vs. an external API), and guiding the AI back on track when it lacks context.

📝 Example Interaction Log
    AI Agent Prompt: "What is one of the strategies to cope with aggressive behaviour online?"

    Tool Called: query_documents
    Tool Input: {"question": "What is one of the strategies to cope with aggressive behaviour online?"}

    Tool Output (Raw Context Returned to Agent):

    Found the following relevant context for the question: 'What is one of the strategies to cope with aggressive behaviour online?'

    --- Source: W18-4401.pdf (Page 1) ---
    Internet, the reach and extent of Internet has given these incidents an unprecedented power and inﬂuence to affect the lives of billions of people... One of the strategies to cope with aggressive behaviour online is to manually monitor and moderate user-generated content, however, the amount and pace at which new data is being created on the web has...

Final AI Agent Answer (Synthesized):
    "Based on the provided documents (W18-4401.pdf, Page 1), one of the primary strategies to cope with aggressive behavior online is to manually monitor and moderate user-generated content."

