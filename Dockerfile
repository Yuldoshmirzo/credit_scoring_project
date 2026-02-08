FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with relaxed constraints
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    optuna \
    mlflow \
    fastapi \
    uvicorn \
    pydantic \
    dvc \
    matplotlib \
    seaborn \
    joblib \
    kagglehub

# Copy project files
COPY . .

# Create artifacts directory
RUN mkdir -p artifacts

# Expose ports
EXPOSE 5000 8000 8001

# Default command
CMD ["/bin/bash"]
