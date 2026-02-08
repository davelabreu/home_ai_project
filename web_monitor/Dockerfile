# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/. .
RUN npm run build

# Stage 2: Backend (Python) Build
FROM python:3.10-slim-bookworm
WORKDIR /app

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker CLI client
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    --no-install-recommends && \
    mkdir -m 0755 -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install network and process utilities required by psutil and arp
RUN apt-get update && apt-get install -y \
    iproute2 \
    net-tools \
    procps \
    sudo \
    dbus-x11 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy the rest of the application code
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Define environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1

# Run app.py when the container launches
CMD ["flask", "run"]