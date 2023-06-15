#!/usr/bin/env python


import argparse
import datetime
import glob
import json
import os
import sys


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--output-root-dir', required=True,
        help="Directoring containing output/")
    parser.add_argument('-p', '--glob-pattern',
        default="**/output.json", help="Directoring containing output/")

    return parser.parse_args()

def find_output_files(root_dir, pattern):
    print("Finding files like {} in {}".format(pattern, root_dir))
    return glob.glob(os.path.join(root_dir, pattern))

def bucket(output_file):
    try:
        with open(output_file) as f:
            data = json.loads(f.read())
        run_ts_obj = datetime.datetime.strptime(data['runtime']['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
        disp_start = data.get('dispersion',{}).get('output', {}).get('start_time')
        if not disp_start:
            return 'na'
        disp_start_obj = datetime.datetime.strptime(disp_start, '%Y-%m-%dT%H:%M:%S')
        if run_ts_obj - disp_start_obj > datetime.timedelta(days=6):
            return 'retro'
        else:
            return 'current'
    except Exception as e:
        print(e)
        return '?'


if __name__ == "__main__":
    args = parse_args()
    files = find_output_files(args.output_root_dir, args.glob_pattern)
    print("Processing {} output files".format(len(files)))
    counts = {}
    for i, f in enumerate(files):
        if i % 10 == 0:
            sys.stdout.write('.')
        b = bucket(f)
        counts[b] = counts.get(b, 0) + 1
    sys.stdout.write('\n')

    for b in counts:
        print("{}: {}".format(b, counts[b]))
