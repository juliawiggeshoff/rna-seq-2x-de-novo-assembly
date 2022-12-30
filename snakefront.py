#!/usr/bin/env python3
## frontend script to manage Snakefile ##

import argparse
import subprocess
import sys
import os
import yaml

parser = argparse.ArgumentParser(description=
                                 "Frontend script to automate launching a Snakemake workflow.",
                                 usage="python %(prog)s --configfile [config/configfile.yaml] --input [config/species_table.tsv] --jobs [N_threads] --adapter [path/to/adapter/file] --lineage [BUSCO_lineage] --maxmemory [max_trinity_memory] --dryrun")
parser.add_argument("-n","--dryrun", 
                    help="Do not execute the workflow, just display what would have been run.",
                    required=False,
                    action="store_true")

parser.add_argument("-i","--input", 
                    help="Tab separated file with three columns for the Species_name, Forward, and Reverse files",
                    metavar=("\b"),
                    required=False)

parser.add_argument("-c", "--configfile",
                    help="Specify or overwrite the config file of the workflow. Can be especified by itself or with other parameters (-i, -a, -l, -m) to set new values in the workflow config object.",
                    metavar=("\b"),
                    required=False) 

parser.add_argument("-j","--jobs", 
                    help="Max number of CPU cores/jobs in parallel if local or cluster/cloud execution.",
                    metavar=("\b"),
                    required=True)    

parser.add_argument("-l","--lineage", 
                    help="BUSCO lineage to use.",
                    metavar=("\b"),
                    required=False) 

parser.add_argument("-a","--adapter", 
                    help="Trimming clip for Trimmomatic and Trinity assembly. Default: TruSeq3-PE.fa",
                    metavar=("\b"),
                    #nargs='?', 
                    #const="TruSeq3-PE.fa", 
                    #default="TruSeq3-PE.fa", 
                    type=str,
                    required=False)   

parser.add_argument("-m","--maxmemory", 
                    help="Max memory size to be used for each sample during the de novo transcriptome assembly from Trinity. Default: 100 GB",
                    metavar=("\b"),
                    #nargs="?", 
                    #const="100G", 
                    #default="100G",
                    type=str,
                    required=False)

args = parser.parse_args()
#print(args,"\n")

if args.configfile:
    try:
        with open(args.configfile, "r") as f:
            parsed_yaml=yaml.safe_load(f)
            #print(parsed_yaml)

        ##if no input file provided in the command line and the sample_info is not empty in args.configfile
        if not args.input:
            if parsed_yaml["sample_info"]:
                if os.path.exists(parsed_yaml["sample_info"]):
                    args.input = parsed_yaml["sample_info"]
                else:
                    sys.exit("The sample table {} provided in {} does not exist. Exiting...".format(parsed_yaml["sample_info"], args.configfile))
        ##if no adapter file provided in the command line and the adapter information is not empty in args.configfile
        if not args.adapter:
            if parsed_yaml["adapter"]:                            
                args.adapter = parsed_yaml["adapter"]
            else:
                print("Warning! No adapter file found in {}. Default set to TruSeq3-PE.fa".format(args.configfile))
                args.adapter = "TruSeq3-PE.fa"
        if not args.maxmemory:
            if parsed_yaml["max_memory"]:
                args.maxmemory = parsed_yaml["max_memory"]
            else:
                print("Warning! No max RAM memory for the Trinity assembly found in {}. Default set to 100G".format(args.configfile))
                args.maxmemory = "100G"
        if not args.lineage:
            if parsed_yaml["lineage"]:
                args.lineage = parsed_yaml["lineage"]
            else:
                print("Warning! No BUSCO lineage found in {}. Default set to mollusca_odb10".format(args.configfile))
                args.lineage = "mollusca_odb10"              
    except FileNotFoundError:
        print("Configuration file not found! Exiting...")
        sys.exit()


if not args.configfile:
    if not args.input:
        sys.exit("No sample table provided! Exiting...")
    if not args.maxmemory:
        print("Warning! No max RAM memory for the Trinity assembly was given. Default set to 100G")
        args.maxmemory="100G"
    if not args.adapter:    
        print("Warning! No adapter file was provided. Default set to TruSeq3-PE.fa")
        args.adapter="TruSeq3-PE.fa"
    if not args.lineage:
        print("Warning! No BUSCO lineage found in {}. Default set to mollusca_odb10".format(args.configfile))
        args.lineage = "mollusca_odb10" 

if args.adapter:
    if "/" in args.adapter:
        if not os.path.exists(args.adapter):
            sys.exit("The adapter file {} could not be found. Exiting...".format(args.adapter))

first_cmd = "snakemake --snakefile workflow/Snakefile_mod --use-conda --jobs {threads} ".format(threads=args.jobs)
remaining_cmd = ""

remaining_cmd += "--dryrun -p " if args.dryrun else ""

remaining_cmd += ("--configfile {} ".format(args.configfile)) if args.configfile else ""

##setting specific config parameters, either new or to overwrite the existing configfile
remaining_cmd += "--config " if args.input or args.adapter or args.maxmemory or args.lineage else ""
remaining_cmd +=("sample_info={} ".format(args.input))
remaining_cmd +=("adapter={} ".format(args.adapter))
remaining_cmd +=("max_memory={} ".format(args.maxmemory))
remaining_cmd +=("lineage={}".format(args.lineage))

full_cmd = first_cmd + remaining_cmd
#print(full_cmd)

subprocess.run(full_cmd, shell=True)
