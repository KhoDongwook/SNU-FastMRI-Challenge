import torch
import argparse
import shutil
import os, sys
from pathlib import Path
import wandb

if os.getcwd() + '/utils/model/' not in sys.path:
    sys.path.insert(1, os.getcwd() + '/utils/model/')
from utils.learning.train_part import train

if os.getcwd() + '/utils/common/' not in sys.path:
    sys.path.insert(1, os.getcwd() + '/utils/common/')
from utils.common.utils import seed_fix

def parse():
    parser = argparse.ArgumentParser(description='Train Varnet on FastMRI challenge Images',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-g', '--GPU-NUM', type=int, default=0, help='GPU number to allocate')
    parser.add_argument('-b', '--batch-size', type=int, default=1, help='Batch size')
    parser.add_argument('-a', '--acc-steps', type=int, default=4, help='Steps of Gradient Accumulation')
    parser.add_argument('-e', '--num-epochs', type=int, default=10, help='Number of epochs')
    parser.add_argument('-l', '--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('-p', '--lr-scheduler-patience', type=int, default=10, help='patience of ReduceLROnPlateau')
    parser.add_argument('-f', '--lr-scheduler-factor', type=float, default=0.1, help='factor of ReduceLROnPlateau')
    parser.add_argument('-r', '--report-interval', type=int, default=20, help='Report interval')
    parser.add_argument('-i', '--save-itr-interval', type=int, default=100, help='itr interval of model save')
    parser.add_argument('-n', '--net-name', type=Path, default='test_varnet', help='Name of network')
    parser.add_argument('-t', '--data-path-train', type=Path, default='/content/drive/MyDrive/Data/val/', help='Directory of train data')
    parser.add_argument('-v', '--data-path-val', type=Path, default='/content/drive/MyDrive/Data/val/', help='Directory of validation data')
    
    parser.add_argument('--cascade', type=int, default=1, help='Number of cascades | Should be less than 12') ## important hyperparameter
    parser.add_argument('--chans', type=int, default=9, help='Number of channels for cascade U-Net | 18 in original varnet') ## important hyperparameter
    parser.add_argument('--sens_chans', type=int, default=4, help='Number of channels for sensitivity map U-Net | 8 in original varnet') ## important hyperparameter
    parser.add_argument('--input-key', type=str, default='kspace', help='Name of input key')
    parser.add_argument('--target-key', type=str, default='image_label', help='Name of target key')
    parser.add_argument('--max-key', type=str, default='max', help='Name of max key in attributes')
    parser.add_argument('--seed', type=int, default=430, help='Fix random seed')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # wandb sweep setting
    sweep_config = {'method': 'random'}
    sweep_config['metric'] = {'name': 'loss', 'goal': 'minimize'}

    parameters_dict = {
      'cascade': {
          'values': [12]
          },
      'chans': {
          'values': [9, 10, 11, 12]
          },
      'sens_chans': {
            'values': [4, 5, 6]
          },
    }
    sweep_config['parameters'] = parameters_dict

    sweep_id = wandb.sweep(sweep_config, project="varnet-sweep-test")

    # wandb sweep
    wandb.agent(sweep_id, train, count=5)
