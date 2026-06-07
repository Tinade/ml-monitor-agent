# Base image — Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js (needed for Phoenix MCP npx command)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn

# Pre-install Phoenix MCP
RUN npx -y @arizeai/phoenix-mcp@latest --version || true

# Copy all project files
COPY . .

# Run the server from src directory
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8080"]
