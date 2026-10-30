"""Exclusive bounded local output; no network or external-data import."""
import json
import os
from .engine import SimulationError


def write(path,value):
    body=(json.dumps(value,allow_nan=False,indent=2)+'\n').encode()
    write_bytes(path,body)


def write_bytes(path,body):
    if len(body)>2*1024*1024:raise SimulationError('output_limit')
    with os.fdopen(os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'wb') as f:f.write(body)
