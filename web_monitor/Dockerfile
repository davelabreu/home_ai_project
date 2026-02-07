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

# Install network and process utilities required by psutil and arp
RUN apt-get update && apt-get install -y \
    iproute2 \
    net-tools \
    procps \
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