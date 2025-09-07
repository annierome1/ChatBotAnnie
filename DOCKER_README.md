# Docker Setup for ChatBot Annie

This project is now containerized for easier deployment and consistent environments.

## Quick Start

### Development Mode
```bash
# Build and start the container
./docker-scripts.sh build
./docker-scripts.sh up

# View logs
./docker-scripts.sh logs

# Stop containers
./docker-scripts.sh down
```

### Production Mode
```bash
# Start production containers
./docker-scripts.sh prod

# Stop production containers
./docker-scripts.sh prod-down
```

## Manual Docker Commands

### Build the image
```bash
cd backend
docker build -t chatbot-annie .
```

### Run the container
```bash
# Development (with volume mounting)
docker run -p 8000:8000 --env-file .env -v $(pwd):/app chatbot-annie

# Production
docker run -p 8000:8000 --env-file .env chatbot-annie
```

### Using Docker Compose
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

Make sure you have a `.env` file in the `backend/` directory with:
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

## Port Configuration

- **Container Port**: 8000 (internal)
- **Host Port**: 8000 (external)
- **Health Check**: `http://localhost:8000/`

## Benefits of Containerization

1. **Consistent Environment**: Same environment locally and in production
2. **Easy Deployment**: Deploy anywhere Docker runs
3. **Isolation**: No conflicts with local Python versions
4. **Scalability**: Easy to scale horizontally
5. **Reproducibility**: Anyone can run the exact same setup

## Troubleshooting

### Check container status
```bash
docker ps
```

### View container logs
```bash
docker logs <container_id>
```

### Access container shell
```bash
docker exec -it <container_id> /bin/bash
```

### Clean up
```bash
./docker-scripts.sh clean
```

## Deployment Options

### Railway
Railway supports Docker deployments. Just push your code and Railway will automatically detect the Dockerfile.

### Other Platforms
- **Heroku**: Use `heroku container:push` and `heroku container:release`
- **AWS ECS**: Use the Docker image in ECS task definitions
- **Google Cloud Run**: Deploy directly from Docker image
- **DigitalOcean App Platform**: Supports Docker deployments

## File Structure
```
ChatBotAnnie/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── ... (your Python files)
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker-scripts.sh
└── DOCKER_README.md
```
