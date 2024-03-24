FROM continuumio/anaconda3:latest

RUN apt-get update && apt-get install -y

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create a log directory
RUN mkdir log
RUN chmod 777 log

# Install any needed packages specified in requirements.txt
RUN conda create -n discord-claude --file discord-claude.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# run the command to start up the application
CMD python application.py
