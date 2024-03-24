FROM continuumio/anaconda3:latest

RUN apt-get update && apt-get install -y

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN conda create -n discord-claude --file discord-claude.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# RUN conda init

# RUN conda activate discord-claude

CMD python application.py
