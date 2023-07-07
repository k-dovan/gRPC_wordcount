from os.path import getsize
import logging
import argparse
import glob
import math
import time
from typing import List, Tuple
from threading import Lock, Event
from concurrent import futures

import grpc
from google.protobuf.empty_pb2 import Empty

import driver_pb2_grpc as services
from driver_pb2 import TaskInfo, TaskType


INPUTS_DIR = 'inputs'


class DriverService(services.DriverServiceServicer):   

    def __init__(self, N: int, M: int):
        self.stop_event = Event()
        self._N = N
        self._M = M
        self._task_lock = Lock()
        self._files_by_map_id = self._assign_files(N)
        self._state = TaskType.Map
        self._task_id = 0
        self._finished_counter = 0
        self._start_time = 0

    def _sorted_input_files(self) -> List[dict]:
        r'''
        Sort input files by size descending.
        '''
        files_with_size = [{"filename": filename, "size": getsize(filename)} for filename in glob.glob(f'{INPUTS_DIR}/*')]
        return sorted(files_with_size, key = lambda x: x["size"], reverse=True)
    
    def _assign_files(self, N: int) -> List[List[str]]:
        r'''
        Assign files to each map task so that the amount of work for each map task as comparable as possible.
        '''        
        def argmin(list):
            return list.index(min(list))

        sorted_files = self._sorted_input_files()
        files_by_map_id = [[] for _ in range(N)]
        workloads_by_map_id = [0]*N                 # wordloads as total bytes of assigned data files
        for file in sorted_files:
            candidate_map_id = argmin(workloads_by_map_id)
            files_by_map_id[candidate_map_id].append(file["filename"])
            workloads_by_map_id[candidate_map_id] += file["size"]
        return files_by_map_id
    
    def _next_map_task(self) -> TaskInfo:
        r'''
        Determines the next Map task and updates the state
        '''
        map_id = self._task_id
        self._task_id += 1

        # Make state NoOp until all the map tasks finish. see FinishMap rpc function
        if map_id == self._N - 1:
            self._state = TaskType.NoOp

        # Store start time in first map task
        if map_id == 0:
            self._start_time = time.time()

        logging.info('starting map %d', map_id)

        return TaskInfo(type=TaskType.Map,
                        id=map_id,
                        filenames=self._files_by_map_id[map_id],
                        M=self._M)

    def _next_reduce_task(self) -> TaskInfo:
        r'''
        Determines the next Reduce task and updates the state
        '''
        bucket_id = self._task_id
        self._task_id += 1

        # Make state NoOp at the end.
        if bucket_id == self._M - 1:
            self._state = TaskType.NoOp

        logging.info('starting reduce %d', bucket_id)

        return TaskInfo(type=TaskType.Reduce, id=bucket_id)

    def RequestTask(self, request: Empty, context: grpc.ServicerContext) -> TaskInfo:
        r'''
        Returns the next task
        '''
        with self._task_lock:
            if self._state == TaskType.Map:
                return self._next_map_task()
            if self._state == TaskType.Reduce:
                return self._next_reduce_task()
            return TaskInfo(type=self._state)

    def FinishMap(self, request: Empty, context: grpc.ServicerContext) -> Empty:
        r'''
        Each worker calls this rpc when finishes a map task 
        '''
        with self._task_lock:
            self._finished_counter += 1

            # Change state to Reduce if all map tasks are finished
            if self._finished_counter == self._N:
                self._state = TaskType.Reduce
                self._task_id = 0
                self._finished_counter = 0
            return Empty()

    def FinishReduce(self, request: Empty, context: grpc.ServicerContext) -> Empty:
        r'''
        Each worker calls this rpc when finished a reduce task
        '''
        with self._task_lock:
            self._finished_counter += 1
            if self._finished_counter == self._M:
                logging.info('finished at %.4f secs!',
                             time.time() - self._start_time)
                self._state = TaskType.ShutDown
                self.stop_event.set()
            return Empty()


def create_server(service: DriverService) -> grpc.Server:
    r'''
    Creates a grpc server with given driver service
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    services.add_DriverServiceServicer_to_server(service, server)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    logging.info("Starting server on %s", listen_addr)
    return server


def serve(service: DriverService) -> None:
    r'''
    Starts a grpc server with given driver service and waits for termination
    '''
    server = create_server(service)
    server.start()
    service.stop_event.wait()
    # Wait to all the workers shut down
    time.sleep(0.5)
    server.stop(0)


def get_args() -> Tuple[int, int]:
    r'''
    Parses N and M from arguments
    '''
    parser = argparse.ArgumentParser(description='Starts the driver.')
    parser.add_argument('-N', dest='N', type=int,
                        required=True, help='Number of Map tasks')
    parser.add_argument('-M', dest='M', type=int,
                        required=True, help='Number of Reduce tasks')
    args = parser.parse_args()
    return args.N, args.M


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s driver %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    N, M = get_args()
    service = DriverService(N, M)
    serve(service)
