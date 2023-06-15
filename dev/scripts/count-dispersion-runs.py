#!/usr/bin/env python


import argparse
import datetime
import fnmatch
import json
import os


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--output-root-dir', required=True,
        help="Directoring containing output/")
    parser.add_argument('-p', '--output-file-pattern',
        default="output.json", help="Directoring containing output/")

    return parser.parse_args()

def find_output_files(root_dir, pattern):
    result = []
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

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
    files = find_output_files(args.output_root_dir, args.output_file_pattern)
    counts = {}
    for f in files:
        b = bucket(f)
        counts[b] = counts.get(b, 0) + 1

    for b in counts:
        print(f"{b}: {counts[b]}")
