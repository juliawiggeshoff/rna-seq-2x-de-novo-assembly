# Rna-Seq to BUSCO - Workflow

Workflow to quality-check RNA-Seq data prior to and post trimming with Trimmomatic. Reads are assembled with two *de novo* transcriptome assemblers, Trinity and Shannon, but more will be added soon. BUSCO is used to annotate and benchmark the assemblies.

## System requirements
### Local machine
- If you don't have it yet, it is necessary to have conda or miniconda in your machine.
Follow [there](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html) instructions.
	- I highly (**highly!**) recommend installing a much much faster package manager to replace conda, [mamba](https://github.com/mamba-org/mamba)
	- In you command-line, type:
	`conda install -n base -c conda-forge mamba` 

- Likewise, follow [this](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) tutorial to install Git if you don't have it.

### HPC system

Follow the instructions from your cluster administrator regarding loading of  modules, such as loading a root distribution from Conda.
For example, with the cluster I work with, we use modules to set up environmental variables, which have to first be loaded within the jobscripts. They modify the $PATH variable after loading the module.

e.g.:
`module load anaconda3/2022.05`

You usually don't have sudo rights to install anything to the root of the cluster. So, as I wanted to work with a more updated distribution of conda and especially use mamba to replace conda as a package manager, I had to first create my own "local" conda, i.e. I first loaded the module and then created a new environment I called localconda 
1. `module load anaconda3/2022.05`
2. `conda create -n localconda -c conda-forge conda=22.9.0`
3. `conda activate localconda`
4. `conda install -n localconda -c conda-forge mamba`

If you run `conda env list` you'll probably see something like this:
`/home/myusername/.conda/envs/localconda/`

## Installation 

1. Clone this repository

`git clone https://gitlab.leibniz-lib.de/jwiggeshoff/rna-seq-to-busco.git`

2. Activate your conda base

`coda activate base`

- If you are working on a cluster or have your own "local", isolated environment you want to activate instead (see [here](https://gitlab.leibniz-lib.de/jwiggeshoff/rna-seq-to-busco#hpc-system)), use its name to activate it

`conda activate localconda`

3. Install **rna-seq-to-busco** into an isolated software environment by navigating to the directory where this repo is and run:

`conda env create --file environment.yaml`

If you followed what I recommended in the [System requirements](https://gitlab.leibniz-lib.de/jwiggeshoff/rna-seq-to-busco#local-machine), run this intead:

`mamba env create --file environment.yaml`

The environment from rna-seq-to-busco is created

4. *Always* activate the environment before running the workflow

On a local machine:

`conda activate rna-seq-to-busco`

If you are on a cluster and/or created the environment "within" another environment, you want to run this first:

`conda env list`

You will probably see something like this among your enviornments:

`home/myusername/.conda/envs/localconda/envs/rna-seq-to-busco`

From no own, you have to give this full path when activating the environment prior to running the workflow

`conda activate /home/myusername/.conda/envs/localconda/envs/rna-seq-to-busco`

## Data requirements

1. Paired-end reads (Forward and Reverse) 

Move your RNA-Seq data into `resources/raw_data`

**Note**: Right now, the workflow only works with species which have paires-end reads. This will modified later. Likewise, a system to automate the SRA data download from NCBI will be implemented

2. Tab-separates, species table

Template table provided in `config/species_table.tsv`. Modify following the name of your species and the filenames from the paired-end reads.

This is important not only to know how the raw data is named, but also to write the names of the files in meaninful ways, i.e. HW03_Berthella_plumula.fasta instead of something like SRR8573930.fasta. Also really important for the final graph from busco report.

**Important**:
- **No cell can be empty**, as Snakemake will see this as missing input file and the analyses will not run
- **Never modify the headers** from the table otherwise the same thing will happen
- The names of the forward and reverse files have to be the same as the actual files you copied into `resources/raw_data`

|Species_name|Forward|Reverse|
|--|--|--|
|HW03_Berthella_plumula|SRR8573930_1.fastq.gz|SRR8573930_2.fastq.gz|

3. Config file

Template found in `config/configfile.yaml`. Modify accordingly.
Required file for important settings from the analyses. Workflow will fail if anything is wrong or missing.

- sample_info: you can keep this path, but remember to modify the information according to your samples (See previous step in the data requirements)
- max_memory: max amount of memory Trinity assembler can use
- adapter: adpater file used by Trimmomatic. You can provide a custom adapter file, like is the case in the template file, or the name from one of the Fasta files supplied by Trimmomatic. The most common one is TruSeq3-PE.fa, as it is used for by HiSeq and
MiSeq machines. See page 12 from the [Trimmomatic manual](http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/TrimmomaticManual_V0.32.pdf) for more information.
- lineage: clade-specific information to identify BUSCO genes in the transcripts. Click [here](https://busco-data.ezlab.org/v5/data/lineages/) for all BUSCO lineages.

# Starting the workflow

Remember to always activate the environment first

`conda activate rna-seq-to-busco`

or

`conda activate /home/myusername/.conda/envs/localconda/envs/rna-seq-to-busco`

## Local machine

**Not recommended** if you don't have a lot of storage and CPUs available (and time to wait...). Nevertheless, you can simply run like this:

`nohup snakemake --keep-going --use-conda --verbose --printshellcmds --reason --nolock --cores 11 > nohup_$(date +"%F_%H").out &`

## HPC system

Two working options were tested to run the workflow in HPC clusters using the Sun Grid Engine (SGE) queue scheduler system

### Before the first execution of the workflow

Run this to create the environments from the rules:

`snakemake --cores 8 --use-conda --conda-create-envs-only`

### Option 1:

`nohup snakemake --keep-going --use-conda --verbose --printshellcmds --reason --nolock --jobs 15 --cores 31 --local-cores 15 --max-threads 25 --cluster "qsub -V -b y -j y -o snakejob_logs/ -cwd -q fast.q,small.q,medium.q,large.q -M user.email@gmail.com -m be" > nohup_$(date +"%F_%H").out &`

Remember to:
1. Create snakejob_logs in the working directory: `mkdir -p snakejob_logs`
2. Modify *user.email@gmail.com*
3. Change values for --jobs, --cores, --local-cores, and --max-threads accordingly 
	- Important: Make sure you set a low value for --local-cores to not take up too much resources from your host node

### Option 2:

A template jobscript `template_run_rna-seq-to-busco.sh` is found under `misc/`

**Important:** Please, modify the qsub options according to your system! 
Features to modify:
- E-mail address: -M *user.email@gmail.com*
- Mailing settings, if needed: -m *be*
- If you  want to to join (write) stderr to stdout, use -j y instead and delete the line for -e, just keepig the option -o
- If you want to, the name of the jobscript: -N *rna-seq-to-busco*
- **Name of parallel environment (PE) as well as the number of maximum threads to use:** -pe *smp 31*
- **Queue name!** (extremely unique to your system): -q *small.q,medium.q,large.q*

Ater modifying the template, copy it (while also modifying its name) to the working directory:

If you are within the folder `misc/`:

`cp template_run_rna-seq-to-busco.sh ../run_rna-seq-to-busco.sh`

You should see within the path where the folders config/, resources/, results/, and workflow/ are, together with files README.md and environment.yaml

Finally, run:

`qsub run_rna-seq-to-busco.sh`

# Finishing the analyses: generating the report

Once your analyses have successfuly finished, you can now use Snakemake one last time to generate a report. It describes the used software versions, the reports from fastqc, the final graph generated by the BUSCO report. It also included the commands as paths to in and output files. To know more, see the documentation from Snakemake [here](https://snakemake.readthedocs.io/en/stable/snakefiles/reporting.html).

1. Remember to activate the environment first

`conda activate rna-seq-to-busco`

or

`conda activate /home/myusername/.conda/envs/localconda/envs/rna-seq-to-busco`

2. Navigate to the directory and type

`snakemake --report report.html`

or 

`snakemake --report report.zip`

You probably want to have the zip file instead if you have a lot of samples, as the reports from FastQC my create a very large file.

# Done :)
