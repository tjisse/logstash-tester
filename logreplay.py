#!/usr/bin/env python
"""
Log Replay: Replay log events for testing logstash configuration
Usage: logreplay.py [-hvn] [-i INPUT_DIR] [-o OUTPUT_DIR] [-t INTERVAL] [-r VARIATION]

-h --help                           show this
-v --version                        show version
-n --no-loop                        do not loop when the end of a log is reached [default: false]
-i --input INPUT_DIR                specify log input dir [default: /tmp/logreplay-input/]
-o --output OUTPUT_DIR              specify log output dir [default: /var/log/]
-t --time-interval INTERVAL         time between log events in seconds (0.1-60.0) [default: 1.0]
-r --random-variation VARIATION     maximum randomized variation in seconds plus and minus [default: 10.0]

"""

from warnings import warn
from docopt import docopt
import os
import shutil
import trollius
from trollius import From
import random

VERSION = 'Log Replay 1.0'
INPUT_FILE_EXTENSIONS = ['.log']


def main(args):
    input_dir = args['--input']
    output_dir = args['--output']
    interval = float(args['--time-interval'])
    no_loop = args['--no-loop']
    random_variation = float(args['--random-variation'])
    print('{}, replaying logs from {} to {}'.format(VERSION, input_dir, output_dir))

    try:
        file_pairs = initialize_files(input_dir, output_dir)
        start_write_loops(file_pairs, interval, random_variation, no_loop)
    except KeyboardInterrupt:
        print('Caught keyboard interrupt, exiting...')
    finally:
        delete_created_files(input_dir, output_dir)


def delete_created_files(input_dir, output_dir):
    ds, fs = [], []
    for _, dirs, files in os.walk(input_dir, onerror=_raise_error):
        ds = dirs
        fs = files
        break
    for d in ds:
        dir_path = os.path.join(output_dir, d)
        shutil.rmtree(dir_path)
    for f in fs:
        file_path = os.path.join(output_dir, f)
        os.remove(file_path)


def initialize_files(input_dir, output_dir):
    file_pairs = []
    if not os.path.isdir(input_dir):
        raise RuntimeError('Input directory {} does not exist'.format(input_dir))
    if not os.listdir(input_dir):
        warn('Input directory {} is empty'.format(input_dir))
    if not os.path.isdir(output_dir):
        raise RuntimeError('Output directory {} does not exist'.format(output_dir))

    for root, dirs, files in os.walk(input_dir, onerror=_raise_error):
        rel_path = os.path.relpath(root, input_dir)
        output_root = os.path.join(output_dir, rel_path)
        for d in dirs:
            dir_path = os.path.join(output_root, d)
            os.mkdir(dir_path)
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in INPUT_FILE_EXTENSIONS:
                input_file, output_file = create_file_pair(root, output_root, f)
                file_pairs.append((input_file, output_file))
    return file_pairs


def create_file_pair(input_root, output_root, filename):
    input_file_path = os.path.join(input_root, filename)
    output_file_path = os.path.join(output_root, filename)
    if not os.access(input_file_path, os.R_OK):
        raise RuntimeError('Input file not readable: {}', input_file_path)
    if not os.access(output_root, os.W_OK):
        raise RuntimeError('Output dir not writable: {}', output_root)
    return input_file_path, output_file_path


def start_write_loops(file_pairs, interval, random_variation, no_loop):
    tasks = []
    if not 0.1 < interval < 100.0:
        raise RuntimeError('Invalid time interval value: {}'.format(interval))
    loop = trollius.get_event_loop()
    for input_file, output_file in file_pairs:
        task = trollius.ensure_future(log_write_loop(input_file, output_file, interval, random_variation, no_loop))
        tasks.append(task)
    loop.run_until_complete(trollius.wait(tasks))


@trollius.coroutine
def log_write_loop(input_file, output_file, interval, random_variation, no_loop):
    if os.stat(input_file).st_size == 0:
        warn('Input file {} is empty'.format(input_file))
        return
    print('Starting write loop for file {}'.format(output_file))
    while True:
        with open(input_file) as i, open(output_file, 'w') as o:
            for line in i:
                print('Writing log entry {} -> {}'.format(input_file, output_file))
                o.write(line)
                sleepy_time = calc_sleepy_time(interval, random_variation)
                yield From(trollius.sleep(sleepy_time))
            if no_loop:
                break


def calc_sleepy_time(interval, random_variation):
    random_mod = random.uniform(-random_variation, random_variation)
    random_iv = interval + random_mod
    return max(0.1, random_iv)


def _raise_error(error):
    raise error


if __name__ == '__main__':
    main(docopt(__doc__, version=VERSION))
