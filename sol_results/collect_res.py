import os
import sys
import argparse

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
      next_run_time = (linesplit[3].split('}'))[0]
      run_norm_list.append(float(next_run_time))
  fd.close()

  print("Download took %.3fs on average for %d" % (sum(download_list)/len(download_list), len(download_list)))
  print("Run Normal took %.3fs on average for %d" % (sum(run_norm_list)/len(run_norm_list), len(run_norm_list)))
  print("Run Fast took %.3fs on average for %d" % (sum(run_fast_list)/len(run_fast_list), len(run_fast_list)))

if __name__ == '__main__':
  main(get_args())
