from binary import BinaryClient
from quark.concurrent import Context

runtime = Context.runtime()

client = BinaryClient(runtime, "ws://127.0.0.1:8910/binary")
