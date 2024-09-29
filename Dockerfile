
# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# If you don't have a requirements.txt file, create one with `streamlit`
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit 

RUN pip install --no-cache-dir langchain
RUN pip install --no-cache-dir langchain-community

# Expose port 8501 to the outside world
EXPOSE 8084

# Command to run Streamlit app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
ENTRYPOINT [ "streamlit", "run", "app.py", "--server.port=8084", "--server.address=0.0.0.0" ]