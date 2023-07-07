import glob
import os
import logging
from typing import List, Dict, Tuple

import grpc
from google.protobuf.empty_pb2 import Empty

from driver_pb2_grpc import DriverServiceStub


INTERMEDIATE_DIR = 'intermediate'
OUT_DIR = 'out'
SERVER_ADDRESS = 'localhost:50051'


class WordCounter:
    r'''
    Stores number of occurrences of each word
    '''

    def __init__(self):
        self._dict: Dict[str, int] = {}

    def count(self, word: int) -> None:
        r'''
        Increases the counter of given word
        '''
        if word not in self._dict:
            self._dict[word] = 0
        self._dict[word] += 1

    def items(self) -> List[Tuple[str, int]]:
        r'''
        Returns words and occurrences
        '''
        return self._dict.items()


class Reducer:
    r'''
    Performs the reduce task
    '''

    def _count_bucket(self, bucket_id: int) -> WordCounter:
        r'''
        Counts each word in bucket intermeriate files
        '''
        wc = WordCounter()
        for bucket_file in glob.glob(f'{INTERMEDIATE_DIR}/mr-*-{bucket_id}'):
            with open(bucket_file) as bf:
                for word in bf.readlines():
                    wc.count(word.strip())
        return wc

    def _finish_reduce(self) -> None:
        r'''
        Calls FinishReduce rpc
        '''
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = DriverServiceStub(channel)
            stub.FinishReduce(Empty())

    def reduce(self, bucket_id: int) -> None:
        r'''
        Reduce Task
        '''
        os.makedirs(OUT_DIR, exist_ok=True)
        logging.info('starting reduce %d', bucket_id)
        wc = self._count_bucket(bucket_id)
        with open(f'{OUT_DIR}/out-{bucket_id}', 'a') as out:
            for word, count in wc.items():
                out.write(f'{word} {count}\n')
        self._finish_reduce()
