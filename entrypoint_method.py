import argparse
import os
import requests
import subprocess

def create_file(out_filename,in_url):
    r = requests.get(in_url, allow_redirects=True)
    open(out_filename, 'wb').write(r.content)

def run_method(output_dir, name, fastq_path, parameters):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, f'{name}.log.txt')

    # Run Kallisto initially
    # ref_dir should point to an .idx file.
    ref_idx = f"01_references/{parameters[0]}/kallisto_transcriptome.idx"
    gtf_pos = f"01_references/{parameters[0]}/genome.gtf"
    ka_outdir = f"{output_dir}/kallisto_out"
    os.makedirs(ka_outdir, exist_ok=True)

    # Create R1 and R2 files by concatenation
    fastq_files = [f for f in os.listdir(fastq_path) if f.endswith(('.fastq', '.fastq.gz'))]
    fastq_files.sort()
    fastq_files = [fastq_path + file for file in fastq_files]
    ka_reads = " ".join(fastq_files)
    
    ka_command = f"kallisto quant -i {ref_idx} -o {ka_outdir} -b 10 -t 32 "
    ka_command += f"--genomebam --gtf {gtf_pos} "
    ka_command += f"{ka_reads}"

    content = f"This is the kallisto command\n{ka_command}\n\n"

    a = subprocess.run(ka_command.split(),capture_output=True,text=True)
    content += f"Kallisto output: (temporarily left out)\n"
    content += a.stdout
    content += f"\n\n"

    ka_outbam_pos = f"{ka_outdir}/pseudoalignments.bam"
    ka_sortbam_pos = f"{output_dir}/{name}.possorted.bam"
    
    # Sort the resulting bam file
    sort_command = f"samtools sort -o {ka_sortbam_pos} {ka_outbam_pos}"
    a = subprocess.run(sort_command.split(),capture_output=True,text=True)
    content += a.stdout
    content += f"\n\n"

    # Move BAM file to output folder
    # mv_bam_command = f"mv {ka_outdir}/outs/possorted_genome_bam.bam {output_dir}/{name}.possorted.bam"
    # a = subprocess.run(mv_bam_command.split(),capture_output=True,text=True)
    # content += a.stdout
    
    # Move expression matrix to reference-folder for comparison (faster runtime later) 
    # * Needs edits
    # cp_matrix_command = f"cp -r {cr_outdir}/outs/filtered_feature_bc_matrix {output_dir}/."
    # a = subprocess.run(cp_matrix_command.split(),capture_output=True,text=True)

    # Remove cellranger folder (the data is not needed downstream, and takes up quite a lot of space)
    # cleanup_command = f"rm -rf {cr_outdir}"
    # a = subprocess.run(cleanup_command.split(),capture_output=True,text=True)

    # genome_path = os.path.join(output_dir, f'{name}.refgenome.txt')
    # a = subprocess.run(f"touch {genome_path}".split(),capture_output=True,text=True)
    # content += a.stdout

    # fasta_path = f"{ref_dir}/fasta/genome.fa"
    # with open(genome_path, 'w') as file:
    #     file.write(fasta_path)

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
    parser.add_argument('--R2.counts',type=str, help='input file #1')

    # Parse arguments
    args, extra_arguments = parser.parse_known_args()

    R1_input = getattr(args, 'R1.counts')
    R2_input = getattr(args, 'R2.counts')
    fastq_paths = os.path.dirname(R1_input) + f"/"

#    process_filtered_input = getattr(args, 'process.filtered')
#    data_counts_input = getattr(args, 'data.counts')
#    data_meta_input = getattr(args, 'data.meta')
#    data_params_input = getattr(args, 'data.data_specific_params')

#    assert process_filtered_input is not None or data_counts_input is not None, "At least one of the values must not be None"
#    data_counts_input = process_filtered_input if process_filtered_input else data_counts_input

    input_files = [R1_input, R2_input]

    # run_method(args.output_dir, args.name, input_files, extra_arguments)
    run_method(args.output_dir, args.name, fastq_paths, extra_arguments)


if __name__ == "__main__":
    main()
