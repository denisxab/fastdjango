# Use an official Python runtime as a parent image
FROM python:3.11-slim

RUN apt update && apt install make

# Set the working directory in the container
WORKDIR /app

# Copy the local requirements file to the container at /app
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD tail -f /dev/null

# ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
