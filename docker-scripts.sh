#!/bin/bash

# Docker management scripts for ChatBot Annie

case "$1" in
    "build")
        echo "Building Docker image..."
        docker-compose build
        ;;
    "up")
        echo "Starting containers..."
        docker-compose up -d
        ;;
    "down")
        echo "Stopping containers..."
        docker-compose down
        ;;
    "logs")
        echo "Showing logs..."
        docker-compose logs -f chatbot-backend
        ;;
    "restart")
        echo "Restarting containers..."
        docker-compose restart
        ;;
    "prod")
        echo "Starting production containers..."
        docker-compose -f docker-compose.prod.yml up -d
        ;;
    "prod-down")
        echo "Stopping production containers..."
        docker-compose -f docker-compose.prod.yml down
        ;;
    "clean")
        echo "Cleaning up Docker resources..."
        docker-compose down
        docker system prune -f
        ;;
    *)
        echo "Usage: $0 {build|up|down|logs|restart|prod|prod-down|clean}"
        echo ""
        echo "Commands:"
        echo "  build     - Build the Docker image"
        echo "  up        - Start containers in development mode"
        echo "  down      - Stop containers"
        echo "  logs      - Show container logs"
        echo "  restart   - Restart containers"
        echo "  prod      - Start containers in production mode"
        echo "  prod-down - Stop production containers"
        echo "  clean     - Clean up Docker resources"
        exit 1
        ;;
esac
