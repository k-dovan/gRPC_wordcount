import glob
import os
import shutil
from typing import Dict
from reducer import WordCounter

INPUTS_DIR = 'inputs'
INTERMEDIATE_DIR = 'intermediate'
OUT_DIR = 'out'

def groundtruth_count() -> Dict[str, int]:
    wc = WordCounter()

    for filename in glob.glob(f'{INPUTS_DIR}/*'):
        with open(filename) as file:
            text: str = file.read()
            for word in text.split():
                wc.count(word)
    return wc._dict


def parse_line(line):
    word, count = line.split()
    count = int(count)
    return word, count

def clean_previous_output():
    shutil.rmtree(INTERMEDIATE_DIR)
    shutil.rmtree(OUT_DIR)

def run_wordcount_services():
    os.system('python worker.py --name 1 &')
    os.system('python worker.py --name 2 &')
    os.system('python worker.py --name 3 &')
    os.system('python worker.py --name 4 &')
    os.system('python driver.py -N 6 -M 4')


def test():
    real_counts = groundtruth_count()
    clean_previous_output()
    run_wordcount_services()
    for filename in glob.glob(f'{OUT_DIR}/*'):
        with open(filename) as file:
            for word, count in map(parse_line, file.readlines()):
                assert word in real_counts, f'{word} is not in real words'
                ground_truth = real_counts.pop(word)
                assert count == ground_truth, f'filename:{filename}, word:{word}: ground-truth={ground_truth}, map_reduce={count}'

    # the dictionary must be empty
    assert not real_counts
