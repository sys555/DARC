# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir poetry && \
    poetry install && \
    apt-get update && \
    apt-get install -y postgresql-client erlang elixir

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME DARC

# Run app.py when the container launches
CMD ["bash", "-c", "source /app/entrypoint.sh"]