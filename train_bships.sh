#!/bin/bash

################################################################################################
### sbatch configuration parameters must start with #SBATCH and must precede any other commands.
### To ignore, just add another # - like so: ##SBATCH
################################################################################################

#SBATCH --partition main			### specify partition name where to run a job. main: all nodes; gtx1080: 1080 gpu card nodes; rtx2080: 2080 nodes; teslap100: p100 nodes; titanrtx: titan nodes
#SBATCH --time 6-10:30:00			### limit the time of job running. Make sure it is not greater than the partition time limit!! Format: D-H:MM:SS
#SBATCH --job-name my_job			### name of the job
#SBATCH --output=job-%J.out			### output log for running job - %J for job number
#SBATCH --gpus=1				### number of GPUs, allocating more than 1 requires IT team's permission

#SBATCH --mail-user=rontoh@post.bgu.ac.il	### user's email for sending job status messages
#SBATCH --mail-type=FAIL			### conditions for sending the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --mem=24G				### ammount of RAM memory, allocating more than 60G requires IT team's permission

### Print some data to output file ###
echo "SLURM_JOBID"=$SLURM_JOBID
echo "SLURM_JOB_NODELIST"=$SLURM_JOB_NODELIST

### Start your code below ####
module load anaconda				### load anaconda module (must be present when working with conda environments)
source activate ships 				### activate a conda environment, replace my_env with your conda environment
python "/sise/home/rontoh/BattleshiPs/train.py" -e $1 -l $2 -v $3 -a $4 -lr $5 -g $6 -bp $7		### this command executes jupyter lab – replace with your own command