# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy code into container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the simulator
CMD ["python", "app.py"]
