FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# ==========================================================
# 2️⃣ Install system dependencies and uv
# ==========================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic-dev \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install uv (faster dependency manager)
RUN pip install --no-cache-dir uv

# ==========================================================
# 3️⃣ Install dependencies
# ==========================================================
COPY requirements.txt .

# Create a virtual environment using uv and install deps
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r updated_requirements.txt

# Add venv to PATH
ENV PATH="/venv/bin:$PATH"

# ==========================================================
# 4️⃣ Copy the project files
# ==========================================================
COPY . .

# ==========================================================
# 5️⃣ Create a non-root user for security
# ==========================================================
RUN useradd -m appuser
USER appuser


EXPOSE 8000

# NOTE: main.py is inside the app directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
