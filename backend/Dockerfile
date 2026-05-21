FROM python:3.11-slim

WORKDIR /app

# Install python deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app code
COPY backend /app
COPY docs /app/docs  

# Environment defaults
ENV REQUIRE_API_KEY=false
ENV BACKEND_API_KEY=
ENV PORT=5000

EXPOSE 5000

# Run the Flask app (no API key required by default)
CMD ["python", "app.py"]

