# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /RockPanda-Chatbot

# Copy the current directory contents into the container at /app
COPY . /RockPanda-Chatbot

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable
#ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t rag-chatbot .
# docker run -d -p 8000:8000 -v ${PWD}:/rag-chatbot --name rag-chatbot rag-chatbot