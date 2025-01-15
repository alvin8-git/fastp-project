# **Fastp-Project**

This repository contains the `fastp-project`, a pipeline for quality control and preprocessing of FASTQ files using `fastp` and `MultiQC`. The project is designed for ease of use with Docker and includes scripts to streamline the workflow.

---

## **Table of Contents**
- [Overview](#overview)
- [Installation](#installation)
  - [Using Docker](#using-docker)
  - [Building Locally](#building-locally)
- [Download from GitHub](#download-from-github)
- [Running the Program](#running-the-program)
  - [Using `docker.sh`](#using-dockersh)
- [Example Workflow](#example-workflow)
- [Advanced Usage](#advanced-usage)
  - [Run Manually with Docker](#run-manually-with-docker)
  - [Run Python Script Directly](#run-python-script-directly)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## **Overview**

The `fastp-project` is a pipeline designed to:
1. Perform quality control on FASTQ files using `fastp`.
2. Generate summary reports using `MultiQC`.

The project includes:
- A **Dockerfile** to containerize the pipeline.
- A **shell script (`docker.sh`)** for simplified execution.
- A **Python script (`fastp.py`)** for dynamic directory management and sample processing.

---

## **Installation**

### **Using Docker**

1. **Install Docker**:
   - Follow the official installation guide for your operating system: [Docker Installation Guide](https://docs.docker.com/get-docker/).

2. **Pull the Prebuilt Docker Image**:
   - Pull the image from Docker Hub:
     ```
     docker pull <your-docker-id>/fastp_image
     ```
     Replace `<your-docker-id>` with the actual Docker Hub username hosting the image.

3. **Build the Docker Image Locally (Optional)**:
   - If you prefer to build the image locally, navigate to the project directory and run:
     ```
     docker build -t fastp_image .
     ```

---

## **Download from GitHub**

To download the program files:

1. Clone this repository to your local machine:
git clone https://github.com/<your-github-username>/fastp-project.git
cd fastp-project
text
Replace `<your-github-username>` with your GitHub username.

2. Verify that the following files are present in the cloned directory:
```
fastp-project/
├── docker.sh # Shell script to run the progam
├── fastp.py # Python script for processing FASTQfiles
├── Dockerfile # Dockerfile for building the container
├── test_data/ # Example test data(optional)
│ ├─sample1.fq.gz
│ ├── sample2.fq.gz
└── README.md #Documentation
```
text

---

## **Running the Program**

### **Using `docker.sh`**

The `docker.sh` script simplifies running the program by handling input/output directories, user permissions, and Docker commands.

#### **Step 1: Prepare Input Data**
Place all your FASTQ files in a directory (e.g., `E200007305/`). Ensure that file names follow a consistent naming convention, such as:
sample1_1.fq.gz (R1 reads)
sample1_2.fq.gz (R2 reads)
text

#### **Step 2: Run `docker.sh`**
Execute the script by passing your input directory as an argument:
./docker.sh ./E200007305/
text
This will:
- Create an output directory named `<input-directory>_output` (e.g., `E200007305_output/`).
- Run the pipeline inside a Docker container.
- Save results (e.g., processed FASTQ files, HTML reports) in the output directory.

#### **Script Options**
You can customize parameters by editing `docker.sh`. Key options include:
- Number of threads (`--thread`) for `fastp`.
- Number of parallel jobs (`-jobs`) for processing multiple samples.
- Adapter sequences (`--adapter_fasta`) if custom adapters are required.

---

## **Example Workflow**

Here’s an example workflow:

1. Prepare an input folder with FASTQ files:
```
E200007305/
├── sample1_1.fq.gz
├── sample1_2.fq.gz
├── sample2_1.fq.gz
└── sample2_2.fq.gz
```
text

2. Run `docker.sh`:
./docker.sh ./E200007305/
text

3. Check output in `E200007305_output/`:
```
E200007305_output/
├── fastp/
│ ├── sample1.html
│ ├── sample1.json
│ ├── sample2.html
│ └── sample2.json
├── L01/
│ ├── sample1_fp_1.fq.gz
│ └── sample1_fp_2.fq.gz
└── multiqc_report.html
```
text

---

## **Advanced Usage**

### **Run Manually with Docker**
If you want to manually run the program without using `docker.sh`, execute these commands:

1. Build or pull the image:
docker build -t fastp_image .
text

2. Run a container with mounted directories:
docker run --rm
-v "$(pwd):/app"
-v "$(pwd)/E200007305_output:/app/E200007305_output"
fastp_image /app/E200007305
-sample /app/sample.txt
-jobs 4
--adapter_fasta /app/MGI_adapters.fasta
--thread 16
text

### **Run Python Script Directly**
If Python is installed on your system, you can run `fastp.py` directly:

1. Install dependencies (if any):
pip install -r requirements.txt # Add this file if needed.
text

2. Execute the script:
python fastp.py ./E200007305/ --thread 16 --adapter_fasta ./MGI_adapters.fasta --jobs 4
text

---

## **Troubleshooting**

| Issue                                   | Cause                                                                                 | Solution                                                                                   |
|-----------------------------------------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Permission denied error                 | Output directory is not writable or lacks proper permissions                          | Ensure correct permissions: `chmod -R 775 <output-directory>`                             |
| Missing input folder                    | Input folder path is incorrect                                                        | Verify that input folder exists and is accessible                                         |
| Authentication failed when pushing code | GitHub no longer supports password authentication for HTTPS                           | Use a Personal Access Token or SSH key for authentication                                 |
| Fastp command not found                 | The container does not have `fastp` installed                                         | Ensure that your Dockerfile installs all required dependencies                            |

---

## **Contributing**

We welcome contributions! To contribute:

1. Fork this repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

---

By following this documentation, users can easily install, configure, and run the `fastp-project`.
