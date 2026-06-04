# Base image — Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js (needed for Phoenix MCP npx command)
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run 
# Pre-install Phoenix MCP
RUN npx -y @arizeai/phoenix-mcp@latest --version || true

# Run the agent
CMD ["python", "agent.py"]
