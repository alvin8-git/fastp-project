# Use Python with Debian Bullseye as the base image
FROM python:3.9-bullseye

# Create a non-root user
RUN useradd -ms /bin/bash fastpuser

# Set the working directory in the container
WORKDIR /app

# Install dependencies and fastp
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget gnupg zlib1g-dev && \
    wget http://opengene.org/fastp/fastp && \
    chmod a+x ./fastp && \
    mv fastp /usr/local/bin/ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install MultiQC
RUN pip install --no-cache-dir multiqc

# Install Bash
RUN apt-get update && apt-get install -y bash

# Create directory and permissions
RUN chmod -R 775 /app

# Copy project files into the container and set ownership
COPY --chown=fastpuser:fastpuser . .

# Set default permissions for all files created by the container
RUN umask 0002

# Copy the necessary files into the container
#COPY main.py /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure /app/output exists and has proper permissions
RUN mkdir -p /app/output && chown -R fastpuser:fastpuser /app/output && chmod -R 775 /app/output

# Switch to the non-root user
USER fastpuser

# Set the default command
ENTRYPOINT ["python", "fastp.py"]

