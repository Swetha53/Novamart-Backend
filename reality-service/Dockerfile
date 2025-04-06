# Use official Python image as the base
FROM python:3.9

# Install system dependencies
RUN #apt-get update && apt-get install -y libgomp1 libgl1-mesa-glx

# Set the working directory in the container
#WORKDIR /app

# Copy the requirements file and install dependencies
#COPY requirements.txt .

RUN #ulimit -n 10000

RUN #pip install --no-cache-dir -r requirements.txt

# Copy the rest of the FastAPI application
#COPY . /app

# Expose the port FastAPI will run on
#EXPOSE 8000

# Command to run the application using Uvicorn
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "server.key", "--ssl-certfile", "server.crt", "--workers", "4"]