# Use community CPU-only PyTorch base image
FROM cnstark/pytorch:2.3.0-py3.10.15-ubuntu22.04

# Disable bytecode generation and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Default port (can be overridden by Azure's $PORT)
EXPOSE 5000

# Entrypoint to launch the Flask app
CMD ["python", "app.py"]

