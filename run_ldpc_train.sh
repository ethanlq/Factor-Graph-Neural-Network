#!/bin/sh
#SBATCH -p batch        	                                # partition (this is the queue your job will be added to)
#SBATCH -N 1               	                                # number of nodes (use a single node)
#SBATCH -n 8             	                                # number of cores (sequential job => uses 1 core)
#SBATCH --time=24:00:00    	                                # time allocation, which has the format (D-HH:MM:SS), here set to 1 hour
#SBATCH --mem=16GB         	                                # specify the memory required per node (here set to 4 GB)
#SBATCH --gres=gpu:1                                            # generic resource required (here requires 4 GPUs)
#SBATCH -M acvt

# Configure notifications
#SBATCH --mail-type=END                                         # Send a notification email when the job is done (=END)
#SBATCH --mail-type=FAIL                                        # Send a notification email when the job fails (=FAIL)
#SBATCH --mail-user=zhen.zhang02@adelaide.edu.au          # Email to which notifications will be sent

module load CUDA/9.2.148.1

cd ${HOME}/FGNN
python train_ldpc_sp_residual.py --train --n_epochs 2000 --model_path model_ldpc/train_syn_hop_factor_FactorNN_snr_None_at_2020-05-16_12\:50\:42/FactorNN_nn_factor_epoches_339_snr_None.pt