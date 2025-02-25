# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Define environment variable for Apprise URLs
ENV APPRISE_URLS=""

# Run notify_on_sale.py when the container launches
CMD ["python", "main.py"]

