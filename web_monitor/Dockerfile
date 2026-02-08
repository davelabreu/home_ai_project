# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/. .
RUN npm run build

# Stage 2: Backend (Python) Build
FROM nvcr.io/nvidia/l4t-base:r36.2.0
WORKDIR /app

# Install Python 3.10 and pip, and other necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    iproute2 \
    net-tools \
    procps \
    sudo \
    dbus-x11 \
    docker.io && \
    rm -rf /var/lib/apt/lists/*

# Set default Python to 3.10
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Explicitly copy application files that can change
COPY app.py .
COPY templates /app/templates
COPY scripts /app/scripts

# Expose the port that Flask will run on
EXPOSE 5000

# Define environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_DEBUG=1

# Run app.py when the container launches
CMD ["flask", "run"]