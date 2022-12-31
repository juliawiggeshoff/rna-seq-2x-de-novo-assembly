#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -j n
#$ -e cluster_logs/
#$ -o cluster_logs/
#$ -q small.q,medium.q,large.q
#$ -N rna-seq-to-busco
#$ -pe smp 41
#$ -M user.email@gmail.com
#$ -m be

module load anaconda3/2022.05
conda activate /home/myusername/.conda/envs/localconda/envs/rna-seq-to-busco

mkdir -p cluster_logs

#one core will be used by snakemake to monitore the other processes
THREADS=$(expr ${NSLOTS} - 1)

snakemake \
    --snakefile workflow/Snakefile \
    --configfile config/configfile.yaml \
    --keep-going \
    --latency-wait 300 \
    --use-conda \
    --cores ${THREADS} \
    --verbose \
    --printshellcmds \
    --reason \
    --nolock     
    #--rerun-triggers mtime
