# 🤖 GenAI RAG Chatbot

A **full-stack Retrieval-Augmented Generation (RAG) chatbot** that allows users to upload PDF documents and ask questions about their content using natural language. Built with FastAPI backend, Streamlit frontend, and powered by OpenAI's GPT models.

![GenAI RAG Chatbot](https://img.shields.io/badge/AI-Powered-blue) ![Docker](https://img.shields.io/badge/Docker-Containerized-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green)

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│   Streamlit     │◄───────────────►│   FastAPI       │
│   Frontend      │                 │   Backend       │
│   (Port 8501)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   OpenAI API    │
                                    │   + FAISS       │
                                    │   Vector Store  │
                                    └─────────────────┘
```

## ✨ Features

- 📄 **PDF Upload & Processing**: Upload and extract text from PDF documents
- 🧠 **AI-Powered Q&A**: Ask natural language questions about document content
- 🔍 **Vector Search**: FAISS-based similarity search for relevant content retrieval
- 💬 **Chat Interface**: User-friendly chat interface with message history
- 📚 **Source Attribution**: View source chunks used to generate answers
- 🐳 **Fully Dockerized**: Easy deployment with Docker Compose
- 🔒 **Secure**: Environment variable-based API key management

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **LangChain**: RAG pipeline and document processing
- **OpenAI**: GPT-3.5-turbo for text generation and embeddings
- **FAISS**: Facebook AI Similarity Search for vector storage
- **PyMuPDF**: PDF text extraction

### Frontend
- **Streamlit**: Interactive web application framework
- **Requests**: HTTP client for API communication

### Infrastructure
- **Docker & Docker Compose**: Containerization and orchestration
- **Python 3.10**: Programming language

## 📁 Project Structure

```
GenAI-RAG-Chatbot/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── document_handler.py     # PDF processing logic
│   ├── g_chain.py             # RAG chain with OpenAI
│   └── utils/
│       ├── __init__.py
│       └── pdf_loader.py      # PDF text extraction
├── frontend/
│   └── frontend.py            # Streamlit interface
├── uploaded_files/            # PDF storage directory
├── vectorstore/              # FAISS index storage
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
├── Dockerfile               # Backend container
├── Dockerfile.streamlit     # Frontend container
├── docker-compose.yml       # Multi-container orchestration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- **OpenAI API Key** (get one from [OpenAI](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:NikhilKaushal20/genai-rag-chatbot.git
   cd genai-rag-chatbot
   ```

2. **Set up environment variables**
   ```bash
   # Copy the provided .env file or create your own
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   nano .env
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications**
   - **Frontend (Streamlit)**: http://localhost:8501
   - **Backend API Docs**: http://localhost:8000/docs
   - **Backend Health Check**: http://localhost:8000/health

## 💻 Usage

### Upload and Process Document

1. Open the Streamlit frontend at `http://localhost:8501`
2. Use the sidebar to upload a PDF file
3. Click "Process PDF" and wait for confirmation
4. The document will be processed and stored in the vector database

### Ask Questions

1. Once a document is processed, use the chat interface
2. Type your question in natural language
3. The AI will search the document and provide an answer
4. View source chunks used to generate the answer in the expandable section

### Example Questions

- "What is the main topic of this document?"
- "Summarize the key findings"
- "What are the conclusions mentioned?"
- "Explain the methodology used"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | GPT model to use | `gpt-3.5-turbo` |
| `CHUNK_SIZE` | Text chunk size for processing | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `VECTOR_SEARCH_K` | Number of similar chunks to retrieve | `4` |

### Customization

- **Modify chunk size**: Edit `CHUNK_SIZE` in `.env` for different document processing
- **Change AI model**: Update `OPENAI_MODEL` to use GPT-4 or other models
- **Adjust retrieval**: Modify `VECTOR_SEARCH_K` for more/fewer source chunks

## 🧪 Development

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run backend locally**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

3. **Run frontend locally**
   ```bash
   cd frontend
   streamlit run frontend.py --server.port 8501
   ```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root |
| `/health` | GET | Health check |
| `/process-pdf` | POST | Upload and process PDF |
| `/query` | POST | Query processed document |

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Upload PDF
curl -X POST "http://localhost:8000/process-pdf" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

# Query document
curl -X POST "http://localhost:8000/query" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this document about?", "filename": "document.pdf"}'
```

## 🐳 Docker Commands

```bash
# Build and run all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Scale services (if needed)
docker-compose up --scale backend=2
```

## 📊 Monitoring and Logs

### View Application Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Health Checks

Both services include health checks:
- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:8501/_stcore/health`

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **Environment Variables**: Use `.env` files for sensitive configuration
- **Docker Secrets**: For production, consider using Docker secrets
- **HTTPS**: Enable HTTPS in production deployments
- **CORS**: Configure CORS settings for production use

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   # Create production .env
   cp .env .env.production
   # Edit production values
   ```

2. **Docker Compose Production**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Nginx Reverse Proxy** (optional)
   ```nginx
   upstream backend {
       server localhost:8000;
   }
   
   upstream frontend {
       server localhost:8501;
   }
   
   server {
       listen 80;
       server_name your-domain.com;
       
       location /api/ {
           proxy_pass http://backend/;
       }
       
       location / {
           proxy_pass http://frontend/;
       }
   }
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure Docker containers are running: `docker-compose ps`
   - Check backend logs: `docker-compose logs backend`

2. **OpenAI API Errors**
   - Verify API key in `.env` file
   - Check API key permissions and billing

3. **PDF Processing Fails**
   - Ensure PDF is not encrypted or corrupted
   - Check file size limits

4. **Vector Store Issues**
   - Clear vector store directory: `rm -rf vectorstore/*`
   - Restart services: `docker-compose restart`

### Getting Help

- Check the [Issues](https://github.com/NikhilKaushal20/genai-rag-chatbot/issues) page
- Create a new issue with detailed error logs
- Contact: [nikhilkaushal20@example.com](mailto:nikhilkaushal20@example.com)

## 🎯 Roadmap

- [ ] Support for multiple document formats (DOCX, TXT)
- [ ] User authentication and document management
- [ ] Advanced filtering and search capabilities
- [ ] Custom embedding models
- [ ] Chat history persistence
- [ ] Multi-language support
- [ ] Integration with cloud storage (AWS S3, Google Drive)

---

**Built with ❤️ by [Nikhil Kaushal](https://github.com/NikhilKaushal20)**