import argparse
import os
import requests
import subprocess

def create_file(out_filename,in_url):
    r = requests.get(in_url, allow_redirects=True)
    open(out_filename, 'wb').write(r.content)

def run_method(output_dir, name, input_files, parameters):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f'{name}.log.txt')

    raw_reads_path = input_files[0]
    anon_fastq_pos = input_files[1]
    
    # Find reference
    # ref_dir should point to an .idx file.
    ref_idx = f"01_references/{parameters[0]}/kallisto_transcriptome.idx"
    gtf_pos = f"01_references/{parameters[0]}/genome.gtf"

    ### Run Kallisto on the anonymized reads ###
    ka_outdir = f"{output_dir}/anon_kallisto_out"
    os.makedirs(ka_outdir, exist_ok=True)

    # Create R1 and R2 files by concatenation
    fastq_files = [f for f in os.listdir(anon_fastq_pos) if f.endswith(('.fastq', '.fastq.gz'))]
    fastq_files.sort()
    fastq_files = [anon_fastq_pos + file for file in fastq_files]
    ka_reads = " ".join(fastq_files)
    
    ka_command = f"kallisto quant -i {ref_idx} -o {ka_outdir} -b 10 -t 32 "
    # ka_command += f"--genomebam --gtf {gtf_pos} "
    ka_command += f"{ka_reads}"

    content = f"This is the anonymized kallisto command\n{ka_command}\n\n"

    a = subprocess.run(ka_command.split(),capture_output=True,text=True)
    content += f"Kallisto output:\n"
    content += a.stdout
    content += f"\n\n"

    ### Run kallisto on the ctrl reads ###
    ka_outdir = f"{output_dir}/ctrl_kallisto_out"
    os.makedirs(ka_outdir, exist_ok=True)

    # Create R1 and R2 files by concatenation
    fastq_files = [f for f in os.listdir(raw_reads_path) if f.endswith(('.fastq', '.fastq.gz'))]
    fastq_files.sort()
    fastq_files = [raw_reads_path + file for file in fastq_files]
    ka_reads = " ".join(fastq_files)
    
    ka_command = f"kallisto quant -i {ref_idx} -o {ka_outdir} -b 10 -t 32 "
    # ka_command += f"--genomebam --gtf {gtf_pos} "
    ka_command += f"{ka_reads}"

    content = f"This is the control kallisto command\n{ka_command}\n\n"

    a = subprocess.run(ka_command.split(),capture_output=True,text=True)
    content += f"Ctrl kallisto output:\n"
    content += a.stdout
    content += f"\n\n"

    # Convert kallisto outputs to seurat objects
    # anon_expr_pos = f""
    # anon_out_pos = f"{output_dir}/{name}_case.rds"
    # anon_R_command = f"Rscript {script_R_file} {anon_out_pos} {anon_expr_pos}"
    # a = subprocess.run(anon_R_command.split(),capture_output=True,text=True)
    # content += f"Anon R command:\n{anon_R_command}\n"

    # ctrl_expr_pos = f""
    # ctrl_out_pos = f"{output_dir}/{name}_ctrl.rds"
    # ctrl_R_command = f"Rscript {script_R_file} {ctrl_out_pos} {ctrl_expr_pos}"
    # a = subprocess.run(ctrl_R_command.split(),capture_output=True,text=True)
    # content += f"Ctrl R command:\n{ctrl_R_command}\n"
    
    # Cleanup unnecessary files
    # cleanup_command = f"rm -rf {anon_ka_outdir}"
    # a = subprocess.run(cleanup_command.split(),capture_output=True,text=True)
    # cleanup_command = f"rm -rf {ctrl_ka_outdir}"
    # a = subprocess.run(cleanup_command.split(),capture_output=True,text=True)

    content += f"All clear - successfull run\n"
    with open(log_file, 'w') as file:
        file.write(content)


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Run method on files.')

    # Add arguments
    parser.add_argument('--output_dir', type=str, help='output directory where method will store results.')
    parser.add_argument('--name', type=str, help='name of the dataset')
    parser.add_argument('--R1.counts',type=str, help='input file #1')
    parser.add_argument('--R2.counts',type=str, help='input file #2')
    parser.add_argument('--anon.reads.path',type=str, help='Path to anonymized reads.')

    # Parse arguments
    args, extra_arguments = parser.parse_known_args()

    R1_input = getattr(args, 'R1.counts')
    R2_input = getattr(args, 'R2.counts')
    anon_reads_path = getattr(args, 'anon.reads.path')
    raw_reads_path = os.path.dirname(R1_input) + f"/"

    # Unpack anonymous read path
    with open(anon_reads_path, 'r') as infile:
        anon_fastq_pos = infile.readline().strip()

    input_files = [raw_reads_path,anon_fastq_pos]

    run_method(args.output_dir, args.name, input_files, extra_arguments)

if __name__ == "__main__":
    main()
