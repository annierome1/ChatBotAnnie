# ChatBot Annie

A sophisticated AI-powered chatbot designed for personal website integration, built with FastAPI and containerized for seamless deployment across environments.

## Overview

ChatBot Annie is an intelligent conversational AI that provides personalized responses based on curated knowledge and context about Annie Rome. The system leverages OpenAI's GPT models for natural language processing and Pinecone for vector-based knowledge retrieval, ensuring accurate and relevant responses.

## Features

- **Intelligent Context Retrieval**: Uses Pinecone vector database to find relevant information from curated knowledge base
- **Streaming Responses**: Real-time response streaming for better user experience
- **CORS Support**: Configured for web frontend integration
- **Containerized Deployment**: Docker-based deployment for consistency across environments
- **Conversation Storage**: Automatic storage of conversations for context and analytics

## Architecture

The chatbot is built using a microservices architecture with the following components:

- **FastAPI Backend**: RESTful API server with async support
- **OpenAI Integration**: GPT model integration for natural language generation
- **Pinecone Vector Database**: Semantic search and knowledge retrieval
- **Docker Containerization**: Consistent deployment environment
- **Streaming Response System**: Real-time message delivery

## Technology Stack

- **Backend**: Python 3.12, FastAPI, Uvicorn
- **AI/ML**: OpenAI GPT API, Pinecone Vector Database
- **Deployment**: Docker, Railway
- **Dependencies**: Asyncio, Python-dotenv, Starlette

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Pinecone API key and index

### Local Development

1. Clone the repository
2. Set up environment variables in `backend/.env`:
   ```
   OPENAI_API_KEY=your_openai_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   PINECONE_INDEX_NAME=your_index_name
   ```

3. Start the development environment:
   ```bash
   ./docker-scripts.sh up
   ```

4. The API will be available at `http://localhost:8000`

### Production Deployment

The application is configured for easy deployment on Railway:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will automatically detect the Dockerfile and deploy

## API Endpoints

- `GET /` - Health check and welcome message
- `POST /chat` - Main chat endpoint for conversation
- `GET /debug` - Debug information (development only)

### Chat Endpoint Usage

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your message here"}'
```

## Docker Management

The project includes helper scripts for easy container management:

```bash
# Start development environment
./docker-scripts.sh up

# Stop containers
./docker-scripts.sh down

# View logs
./docker-scripts.sh logs

# Restart containers
./docker-scripts.sh restart

# Clean up resources
./docker-scripts.sh clean
```

## Configuration

### CORS Settings

The API is configured to accept requests from:
- `http://localhost:3001`
- `http://localhost:5001`
- `https://www.anniecaroline.com`

### Environment Variables

All sensitive configuration is managed through environment variables for security and flexibility.

## Development

### Project Structure

```
ChatBotAnnie/
├── backend/
│   ├── api.py              # FastAPI application and routes
│   ├── chatbot.py          # Core chatbot logic and streaming
│   ├── openai_client.py    # OpenAI API integration
│   ├── pinecone_client.py  # Pinecone vector database client
│   ├── utils.py            # Utility functions
│   ├── Dockerfile          # Container configuration
│   └── requirements.txt    # Python dependencies
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
└── docker-scripts.sh       # Container management scripts

## License

This project is for personal use and website integration.
