# Distributed Map-Reduce Word-Count with gRPC

## GRPC SERVICE API (`driver.proto`)

### RequestTask

Each `Idle` worker, requests driver a task, and the driver decides to send one of the following responses:

- `Map task`: contains `map_id`, `a list of files` to map and `M`
- `Reduce task`: contains reduce id (`bucket_id`) to reduce intermediate files with given `bucket_id`
- `NoOp`: tells to the worker to do nothing (Used when there's no map/reduce task left to assign, but all of them are not finished yet)
- `ShutDown`: tells the worker to shut itself down

### FinishMap

When a worker finishes its map task, calls this rpc. This is important for driver to know when all map tasks are finished and start reduce tasks.

### FinishReduce

When a worker finishes its reduce task, calls this rpc. This is important for driver to know when all reduce tasks are finished and shut down the workers and itself.

**You can compile the protobuf file using the following command:**

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. driver.proto
```

## Driver (`driver.py`)

### **Strategy to assign files to map tasks:**

The easiest way to assign input files to map tasks is to employ round robin algorithm. However, this algorithm can hurt the performance of the program if we have input files with size-imblanced distribution.

To tackle this issue, we sort the input files by size descending and consecutively assign each of them (one at a time) to the map task whose total bytes of already-assigned files are smallest. This way, we can have all map tasks with amount of work comparable to each other.

**Note**: With this strategy, we must accept to consume part of the computational resources for sorting and allocating files for each map task. Especially, when the number of files we need to process increase exponentially.

## Worker (`worker.py`)

The workers wait for the driver to start. Then, they call the `RequestTask` rpc in a loop and do the following according to the task type.

- `Map`: To map input files into the intermediate files;

- `Reduce`: To reduce the given bucket id;

- `NoOp`: The worker does nothing in this loop (for cases when all map/reduce tasks are in progess but not finished yet);

- `ShutDown`: The worker shut itself down.

# How to run
## Install the dependencies

```bash
pip install -r requirements.txt
```

## Run a worker

Note: *Name is just used in the logging to identify each worker (That argument is optional)*

```bash
python worker.py [-h|--help] [--name NAME]
```

## Run the driver

```bash
python driver.py [-h|--help] -N N -M M
```

## Run with bash

```bash
./run.sh
```

## Run the test

```bash
pytest test.py
```

