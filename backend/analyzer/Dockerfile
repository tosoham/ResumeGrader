# inside backend/analyzer/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy everything from backend/analyzer (because this is Render's build context)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional)
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
