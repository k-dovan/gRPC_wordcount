# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: driver.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0c\x64river.proto\x12\twordcount\x1a\x1bgoogle/protobuf/empty.proto\"W\n\x08TaskInfo\x12!\n\x04type\x18\x01 \x01(\x0e\x32\x13.wordcount.TaskType\x12\n\n\x02id\x18\x02 \x01(\r\x12\t\n\x01M\x18\x03 \x01(\r\x12\x11\n\tfilenames\x18\x04 \x03(\t*7\n\x08TaskType\x12\x07\n\x03Map\x10\x00\x12\n\n\x06Reduce\x10\x01\x12\x08\n\x04NoOp\x10\x02\x12\x0c\n\x08ShutDown\x10\x03\x32\xce\x01\n\rDriverService\x12<\n\x0bRequestTask\x12\x16.google.protobuf.Empty\x1a\x13.wordcount.TaskInfo\"\x00\x12=\n\tFinishMap\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\"\x00\x12@\n\x0c\x46inishReduce\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'driver_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_TASKTYPE']._serialized_start=145
  _globals['_TASKTYPE']._serialized_end=200
  _globals['_TASKINFO']._serialized_start=56
  _globals['_TASKINFO']._serialized_end=143
  _globals['_DRIVERSERVICE']._serialized_start=203
  _globals['_DRIVERSERVICE']._serialized_end=409
# @@protoc_insertion_point(module_scope)
