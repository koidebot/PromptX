# PromptX Deployment Guide

## Overview

This guide covers deploying PromptX using GitHub Actions for CI/CD and Docker for containerization.

## Prerequisites

- GitHub repository with Actions enabled
- Docker and Docker Compose installed on target server
- Domain name (optional, for HTTPS)
- OpenAI API key

## Environment Setup

1. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

2. Set required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `GITHUB_REPOSITORY`: Your GitHub repository (username/repo-name)

## GitHub Actions Workflow

The deployment workflow (`.github/workflows/deploy.yml`) includes:

1. **Test Stage**: Runs backend tests and frontend linting
2. **Build Stage**: Builds and pushes Docker images to GitHub Container Registry
3. **Deploy Stage**: Placeholder for deployment commands

### Required GitHub Secrets

Configure these in your repository settings:

- `OPENAI_API_KEY`: OpenAI API key for production
- `JWT_SECRET_KEY`: JWT secret for production
- `BACKEND_URL`: Production backend URL

## Production Deployment

### Option 1: Docker Compose (Recommended)

1. On your server, create deployment directory:
```bash
mkdir promptx-deploy && cd promptx-deploy
```

2. Copy production compose file:
```bash
wget https://raw.githubusercontent.com/your-username/promptx/main/docker-compose.prod.yml
```

3. Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
export JWT_SECRET_KEY="your-secret"
export GITHUB_REPOSITORY="your-username/promptx"
```

4. Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Individual Docker Containers

```bash
# Pull latest images
docker pull ghcr.io/your-username/promptx-backend:latest
docker pull ghcr.io/your-username/promptx-frontend:latest

# Run backend
docker run -d --name promptx-backend \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e JWT_SECRET_KEY="your-secret" \
  ghcr.io/your-username/promptx-backend:latest

# Run frontend
docker run -d --name promptx-frontend \
  -p 80:80 \
  -e VITE_BACKEND_URL="http://your-domain:8000" \
  ghcr.io/your-username/promptx-frontend:latest
```

## HTTPS Setup (Optional)

For production with HTTPS, configure nginx with SSL certificates:

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Update `nginx.conf` with SSL configuration
3. Mount certificates in `docker-compose.prod.yml`

## Monitoring and Health Checks

The backend includes a health check endpoint at `/health`. The production setup includes:

- Health checks for backend container
- Restart policies for all services
- Persistent volume for backend data

## Scaling

To scale the application:

1. **Horizontal scaling**: Run multiple backend instances behind a load balancer
2. **Database**: Replace SQLite with PostgreSQL for production workloads
3. **Caching**: Add Redis for session storage and caching

## Troubleshooting

### Common Issues

1. **Container startup fails**: Check environment variables and logs
2. **API calls fail**: Verify OPENAI_API_KEY is set correctly
3. **Frontend can't reach backend**: Check VITE_BACKEND_URL configuration

### Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update to latest images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

- Use strong JWT secret keys
- Keep OpenAI API key secure
- Enable HTTPS in production
- Regularly update Docker images
- Monitor API usage and costs