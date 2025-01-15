import os
import sys
import glob
import subprocess
from pathlib import Path
import argparse
from multiprocessing import Pool

if len(sys.argv) > 1:
    input_folder = sys.argv[1]
    if os.path.isdir(input_folder):
        print(f"Processing input folder: {input_folder}")
    else:
        print(f"{input_folder} is not a valid directory.")
else:
    print("No input folder specified.")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run fastp followed by MultiQC on FASTQ files.")
    parser.add_argument("input_folder", help="Folder containing FASTQ files.")
    parser.add_argument("-sample", help="Optional file with a list of barcodes to process.", default=None)
    parser.add_argument("-jobs", type=int, help="Number of parallel jobs (default: 1).", default=1)
    parser.add_argument("--adapter_fasta", help="Path to adapter fasta file.", default=None)
    parser.add_argument("--thread", type=int, help="Number of threads for fastp (default: 3).", default=3)
    return parser.parse_args()

def create_output_dir(input_folder):
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(output_dir, 0o775)  # Set permissions to 777
        print(f"Created output directory: {output_dir}")
    except PermissionError as e:
        print(f"PermissionError: {e}. Ensure the directory is writable.")
        sys.exit(1)
    return output_dir

def get_samples_from_file(sample_file):
    with open(sample_file, "r") as f:
        return [line.strip() for line in f if line.strip()]

def find_fastq_files(input_folder):
    return glob.glob(str(input_folder / "**/*.fq.gz"), recursive=True)

def check_paired_reads(r1_file, r2_file):
    def count_reads(file):
        with subprocess.Popen(["zcat", file], stdout=subprocess.PIPE) as proc:
            return sum(1 for _ in proc.stdout) // 4

    r1_count = count_reads(r1_file)
    r2_count = count_reads(r2_file)

    if r1_count != r2_count:
        raise ValueError(f"Mismatched read counts for paired files: {r1_file} ({r1_count} reads) and {r2_file} ({r2_count} reads).")

def run_fastp_for_sample(args):
    sample, files, output_dir, html_dir, adapter_fasta, thread_count = args
    r1_file = next((f for f in files if f.endswith("_1.fq.gz")), None)
    r2_file = next((f for f in files if f.endswith("_2.fq.gz")), None)

    if not r1_file or not r2_file:
        print(f"Skipping {sample}: Missing R1 or R2 files.")
        return

    try:
        check_paired_reads(r1_file, r2_file)
    except ValueError as e:
        print(f"Error for sample {sample}: {e}")
        return

    output_r1 = output_dir / f"{sample}_fp_1.fq.gz"
    output_r2 = output_dir / f"{sample}_fp_2.fq.gz"
    html_output = html_dir / f"{sample}.html"
    json_output = html_dir / f"{sample}.json"

    fastp_cmd = [
        "fastp",
        "-i", r1_file,
        "-I", r2_file,
        "-o", str(output_r1),
        "-O", str(output_r2),
        "--html", str(html_output),
        "--json", str(json_output),
        "--thread", str(thread_count)
    ]

    if adapter_fasta:
        fastp_cmd.extend([
            "--adapter_sequence", "AAGTCGGAGGCCAAGCGGTCTTAGGAAGACAA",
            "--adapter_sequence_r2", "AAGTCGGAGGCCAAGCGGTCTTAGGAAGACAA",
            "--adapter_fasta", adapter_fasta
        ])

    print(f"Running fastp for sample {sample}...")
    subprocess.run(fastp_cmd)

def main():

    # Get output directory from environment variable or set default
    output_base = Path(os.getenv('OUTPUT_DIR', './output'))
    
    # Create output directory if it doesn't exist
    try:
        output_base.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        print(f"PermissionError: {e}. Ensure the directory is writable.")
        sys.exit(1)

    args = parse_arguments()
    input_folder = Path(args.input_folder)
    if not input_folder.is_dir():
        print(f"Error: Input folder '{input_folder}' does not exist.")
        sys.exit(1)

    # Dynamically create the base output directory
    output_base = create_output_dir(input_folder)

    # Define subdirectories for fastp and MultiQC
    fastp_dir = output_base / "fastp"
    #multiqc_dir = output_base / "multiqc_data"
    l01_dir = output_base / "L01"

    for directory in [fastp_dir, l01_dir]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            print(f"PermissionError: {e}. Ensure the directory is writable.")
            sys.exit(1)

    print(f"All output will be saved under: {output_base}")

    # Your processing logic should now use the directories:
    # - fastp_dir for fastp outputs
    # - multiqc_dir for MultiQC outputs
    # - l01_dir for L01 outputs

    # Example placeholders for output generation
    print(f"Fastp outputs will be in: {fastp_dir}")
    #print(f"MultiQC data will be in: {multiqc_dir}")
    print(f"L01 outputs will be in: {l01_dir}")
    
    sample_file = args.sample
    parallel_jobs = args.jobs
    adapter_fasta = args.adapter_fasta
    thread_count = args.thread

    # Get list of barcodes
    barcodes = []
    if sample_file:
        barcodes = get_samples_from_file(sample_file)
    else:
        fastq_files = find_fastq_files(input_folder)
        barcodes = sorted(set(
            f.split("_")[2]
            for f in map(lambda p: Path(p).name, fastq_files)
            if "undecoded" not in f
        ))

    if not barcodes:
        print("No valid barcodes found.")
        sys.exit(1)

    # Find lanes and flowcell ID from the input folder structure
    flowcell_id = input_folder.name
    fastq_files = find_fastq_files(input_folder)

    # Map samples to FASTQ files dynamically from barcodes
    sample_to_files = {}
    for fq_file in fastq_files:
        filename = Path(fq_file).name
        for barcode in barcodes:
            if f"_{barcode}_" in filename:
                parts = filename.split("_")
                if len(parts) < 3:
                    continue
                lane = parts[1]
                sample = f"{flowcell_id}_{lane}_{barcode}"
                if sample not in sample_to_files:
                    sample_to_files[sample] = []
                sample_to_files[sample].append(fq_file)

    # Create output directories dynamically based on flowcell ID and lane
    output_base = Path(os.getenv('OUTPUT_DIR', f"{flowcell_id}_fp"))  # Use environment variable or default name
    output_base.mkdir(parents=True, exist_ok=True)
    
    html_dir = output_base / "fastp"
    html_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    
    for sample, files in sample_to_files.items():
        parts = sample.split("_")
        if len(parts) < 3:
            continue
        lane = parts[1]
        
        # Create lane-specific output directory under base output directory
        output_dir = output_base / lane
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tasks.append((sample, files, output_dir, html_dir, adapter_fasta, thread_count))

    # Run fastp
    if parallel_jobs > 1:
        with Pool(parallel_jobs) as pool:
            pool.map(run_fastp_for_sample, tasks)
    else:
        for task in tasks:
            run_fastp_for_sample(task)

    # Run MultiQC using the base output directory
    print(f"Running MultiQC for {output_base}...")
    subprocess.run(["multiqc", str(output_base), "-o", str(output_base)])

if __name__ == "__main__":
    main()

