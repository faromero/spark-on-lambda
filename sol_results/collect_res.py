import os
import sys
import argparse
import numpy as np

def get_args():
  ap = argparse.ArgumentParser()
  ap.add_argument('--res_file', '-r', required=True,
      dest='res_file', 
      help='Results file to parse')

  return ap.parse_args()

def main(args):
  inp_file = args.res_file

  run_fast_list = []
  run_norm_list = []
  download_list = []
  unzip_list    = []

  fd = open(inp_file, 'r')
  for line in fd:
    if 'RunSparkFast' in line:
      linesplit = (line.split(':'))[2]
      next_run_time = linesplit.split('}')[0]
      run_fast_list.append(float(next_run_time))
    elif 'DownloadSpark' in line:
      linesplit = line.split(':')
      next_download_time = linesplit[2].split(',')[0]
      download_list.append(float(next_download_time))
      next_unzip_time = (linesplit[3].split(','))[0]
      unzip_list.append(float(next_unzip_time))
      next_run_time = (linesplit[4].split('}'))[0]
      run_norm_list.append(float(next_run_time))
  fd.close()


  # Only need to check one of the three
  if len(download_list) != 0:
    # Convert all to numpy arrays
    np_download_list = np.asarray(download_list)
    np_unzip_list = np.asarray(unzip_list)
    np_run_norm_list = np.asarray(run_norm_list)
  
    print("Download took %.2fs on average +- %.2fs for %d" % 
        (np.mean(np_download_list), np.std(np_download_list), np_download_list.size))
    print("Unzip took %.2fs on average +- %.2fs for %d" % 
        (np.mean(np_unzip_list), np.std(np_unzip_list), np_unzip_list.size))
    print("Run Normal took %.2fs on average +- %.2fs for %d" % 
        (np.mean(np_run_norm_list), np.std(np_run_norm_list), np_run_norm_list.size))

  if len(run_fast_list) != 0:
    # Convert to numpy array
    np_run_fast_list = np.asarray(run_fast_list)

    print("Run Fast took %.2fs on average +- %.2fs for %d" % 
        (np.mean(np_run_fast_list), np.std(np_run_fast_list), np_run_fast_list.size))

if __name__ == '__main__':
  main(get_args())
