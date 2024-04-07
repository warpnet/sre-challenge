FROM python:3.10-alpine3.19

# Create the django dir
RUN mkdir /app

# Use this dir for more commands
WORKDIR /app

# Copy the requirements so it can install them
ADD requirements.txt /app/requirements.txt

# Update pip before installing packages
RUN python -m pip install --upgrade pip

# Install required packages
RUN pip install -r requirements.txt
