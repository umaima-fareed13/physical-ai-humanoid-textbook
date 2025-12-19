# Physical AI Textbook - RAG Chatbot Backend

FastAPI backend for the RAG-powered chatbot that helps users learn from the Physical AI Textbook.

## Tech Stack

- **FastAPI** - API framework
- **OpenAI** - Embeddings (text-embedding-3-small) and Chat (gpt-4o-mini)
- **Qdrant Cloud** - Vector database for document retrieval
- **Neon Postgres** - Session and conversation storage

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# OpenAI - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud - Get from https://cloud.qdrant.io/
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Postgres - Get from https://neon.tech/
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Application Settings
DOCS_PATH=../docs
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 4. Start the Server

```bash
# From the backend directory
uvicorn app.main:app --reload --port 8000

# Or from the project root
npm run backend:dev
```

### 5. Ingest Documents

Before using the chatbot, ingest the textbook content:

```bash
# Using curl
curl -X POST http://localhost:8000/ingest

# Or from project root
npm run backend:ingest
```

## API Endpoints

### Chat

**POST `/chat`**

Send a message and get a RAG-powered response.

```json
{
  "message": "What is ROS 2?",
  "session_id": "uuid-from-browser",
  "selected_text": "optional highlighted text"
}
```

Response:
```json
{
  "response": "ROS 2 (Robot Operating System 2) is...",
  "sources": [
    {
      "file": "chapter-1.md",
      "chunk": "relevant text snippet...",
      "score": 0.85
    }
  ],
  "session_id": "uuid-from-browser"
}
```

**GET `/chat/history/{session_id}`**

Get conversation history for a session.

**DELETE `/chat/history/{session_id}`**

Clear conversation history.

### Ingest

**POST `/ingest`**

Ingest all markdown files from the docs directory.

Optional body:
```json
{
  "file": "chapter-1.md"
}
```

**GET `/ingest/status`**

Get vector database status and available documents.

**DELETE `/ingest`**

Clear all vectors (for re-ingestion).

### Health

**GET `/`** or **GET `/health`**

Health check endpoints.

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── config.py         # Settings
│   ├── routers/
│   │   ├── chat.py       # Chat endpoints
│   │   └── ingest.py     # Ingest endpoints
│   ├── services/
│   │   ├── database.py   # Neon Postgres
│   │   ├── embeddings.py # OpenAI embeddings
│   │   ├── rag.py        # RAG logic
│   │   └── vectordb.py   # Qdrant operations
│   ├── models/
│   │   ├── database.py   # SQLAlchemy models
│   │   └── schemas.py    # Pydantic schemas
│   └── utils/
│       └── markdown.py   # Document parsing
├── requirements.txt
├── .env.example
└── README.md
```

### Keeping Vectors in Sync

After updating documentation, re-run ingestion:

```bash
curl -X POST http://localhost:8000/ingest
```

This will:
1. Delete the existing Qdrant collection
2. Re-create it fresh
3. Process all .md files
4. Generate new embeddings
5. Store in Qdrant

## Troubleshooting

### Common Issues

1. **"Cannot connect to Qdrant"**
   - Verify QDRANT_URL and QDRANT_API_KEY in .env
   - Check Qdrant Cloud dashboard for cluster status

2. **"OpenAI API error"**
   - Verify OPENAI_API_KEY is valid
   - Check API usage limits at platform.openai.com

3. **"Database connection failed"**
   - Verify NEON_DATABASE_URL format
   - Ensure Neon database is active (free tier pauses after inactivity)

4. **"No documents found"**
   - Check DOCS_PATH points to correct directory
   - Verify .md files exist in docs/
