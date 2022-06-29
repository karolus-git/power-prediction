FROM python:3.8.10-slim

# Creation of the working directory called dashboard
WORKDIR dashboard

# Build a directory for the dbs
RUN mkdir datasets
RUN mkdir models
RUN mkdir logs

# Update debian
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get -y install gcc mono-mcs && \
    rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --upgrade pip

# Install required packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy of the required source files and the requirements in the working folder
COPY src/assets ./assets
COPY src/app.py .
COPY src/cleaner.py .
COPY src/collector.py .
COPY src/config.py .
COPY src/converter.py .
COPY src/journal.py .
COPY src/layout.py .
COPY src/models.py .
COPY src/pipeline.py .
COPY src/selector.py .
COPY src/store.py .
COPY src/visualization.py .

# Run the unicorn server on the specified ip and port
# The 600sec large timeout is required to download ~60Mo datasets
CMD [ "gunicorn", "--workers=1", "--timeout=600", "--threads=1", "-b 0.0.0.0:8050", "app:server"]
