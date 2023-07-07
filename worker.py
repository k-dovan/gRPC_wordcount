import time
import logging
import argparse
from enum import Enum

import grpc
from google.protobuf.empty_pb2 import Empty

from mapper import Mapper
from reducer import Reducer
from driver_pb2_grpc import DriverServiceStub
from driver_pb2 import TaskType, TaskInfo


SERVER_ADDRESS = 'localhost:50051'


class WorkerState(Enum):
    Waiting = 0     # Waiting for driver to start
    Idle = 1        # Given task is NoOp
    Working = 2     # Doing a Map or Reduce task


class Worker:

    def __init__(self):
        self._state = WorkerState.Working
        self._mapper = Mapper()
        self._reducer = Reducer()

    def _noop(self):
        r'''
        NoOp task
        '''
        # Just one time log idle
        if self._state != WorkerState.Idle:
            logging.info('idle')

    def _request_task(self) -> TaskInfo:
        r'''
        Calls RequestTask rpc
        '''
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = DriverServiceStub(channel)
            task = stub.RequestTask(Empty())
        return task

    def run(self) -> None:
        r'''
        Runs the worker and calls RequestTask rpc until shut down signal
        '''
        while True:
            try:
                task = self._request_task()
                if task.type == TaskType.Map:
                    self._state = WorkerState.Working
                    self._mapper.map(task.id, task.filenames, task.M)

                elif task.type == TaskType.Reduce:
                    self._state = WorkerState.Working
                    self._reducer.reduce(task.id)

                elif task.type == TaskType.NoOp:
                    self._noop()
                    self._state = WorkerState.Idle

                else:   # shut down
                    return
            except grpc._channel._InactiveRpcError:
                # Just one time log driver is unavailable
                if self._state != WorkerState.Waiting:
                    logging.info('driver is unavailable')
                    self._state = WorkerState.Waiting


def get_args() -> str:
    r'''
    Parses name from arguments
    '''
    parser = argparse.ArgumentParser(description='Starts a worker.')
    parser.add_argument('--name', dest='name', default='', help='worker name')
    args = parser.parse_args()
    return args.name


if __name__ == '__main__':
    name = get_args()
    logging.basicConfig(format=f'%(asctime)s worker_{name} %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    worker = Worker()
    worker.run()
