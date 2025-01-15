## build docker image
# docker build -t fastp_image .
## debug container
# docker run -it --rm --entrypoint /bin/bash fastp_image

#!/bin/bash

# Input directory (passed as the first argument)
DIRECTORY=$1

# Validate input directory
if [ -z "$DIRECTORY" ]; then
    echo "Error: No input directory specified."
    exit 1
elif [ ! -d "$DIRECTORY" ]; then
    echo "Error: Specified input directory does not exist."
    exit 1
fi

# Get the base name of the input directory
BASE_NAME=$(basename "$DIRECTORY")

# Set the output directory name dynamically
OUTPUT_DIR="${BASE_NAME}_output"

# Create the output directory and ensure permissions
mkdir -p "$OUTPUT_DIR"
chmod -R 775 "$OUTPUT_DIR" # Ensure it's writable
if [ ! -w "$OUTPUT_DIR" ]; then
    echo "Error: Output directory '$OUTPUT_DIR' is not writable."
    exit 1
fi



# Get the host user and group IDs
USER_ID=$(id -u)
GROUP_ID=$(id -g)
#echo "User ID: $USER_ID"
#echo "Group ID: $GROUP_ID"


# Run the Docker container
docker run --rm \
  -v "$(pwd):/app" \
  -v "$(pwd)/${OUTPUT_DIR}:/app/${OUTPUT_DIR}" \
  -e OUTPUT_DIR="/app/$OUTPUT_DIR" \
  -e HOST_UID=$USER_ID \
  -e HOST_GID=$GROUP_ID \
  --user $USER_ID:$GROUP_ID \
  fastp_image "/app/${BASE_NAME}" \
  -sample /app/sample.txt \
  -jobs 4 \
  --adapter_fasta /app/MGI_adapters.fasta \
  --thread 16
