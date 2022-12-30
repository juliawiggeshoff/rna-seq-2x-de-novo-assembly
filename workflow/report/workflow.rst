This workflow includes a simple workflow tasked with analyzing the quality of RNA-seq data with FastQC prior to and post quality trimming, which is done with trimmomatic.

Two separate de novo transcriptome assembly tools, Trinity and Shannon, are used to put together the reads into continuous sequences.

Finally, BUSCO assesses the completeness of these transcriptomes and outputs a graphical summary of these results per species.

The graphics from BUSCO are found in this report, as well as the results from FastQC. Information on the software versions and the commands used to generate the output files with certain inputs are also detailed.

The project includes a frontend script, snakefront.py, tasked with improving the use of the workflow by users unfamiliar with snakemake.
