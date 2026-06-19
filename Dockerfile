# Use an official lightweight Python image as the base.
# "slim" means it strips out things like compilers and docs — smaller image size.
FROM python:3.12-slim

# Set the working directory inside the container.
# All subsequent commands run from here, and your code will live here.
WORKDIR /app

# Copy requirements first — before copying the rest of the code.
# Docker caches each step. If requirements.txt hasn't changed, Docker
# skips the pip install step entirely on the next build. Faster rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project into the container.
# .dockerignore controls what gets excluded (venv, db files, etc.)
COPY . .

# Create the raw/ directory inside the container.
# It won't exist yet since raw CSVs are in .dockerignore (they're generated).
RUN mkdir -p raw feature_store

# Default command — overridden per-service in docker-compose.yml
CMD ["python", "-c", "print('LocalPulse container ready')"]
