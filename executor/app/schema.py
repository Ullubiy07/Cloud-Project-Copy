from pydantic import BaseModel, root_validator
from typing import List, Union
import json

from subprocess import CompletedProcess
from config import OUTPUT_LIMIT

class File(BaseModel):
    name: str
    content: str

class Flags(BaseModel):
    timeout: bool = False
    mem_out: bool = False
    scan_error: bool = False
    build_error: bool = False
    run_error: bool = False

class Metrics(BaseModel):
    build_time: str = "0.00 s"
    build_memory: str = "0.00 Mb"
    run_time: str = "0.00 s"
    run_memory: str = "0.00 Mb"

class RunRequest(BaseModel):
    language: str
    entry_file: str
    files: List[File]
    stdin: str

class ScanRequest(BaseModel):
    language: str
    files: List[File]

class Requests(BaseModel):
    handle: str
    body: Union[RunRequest, ScanRequest]

    @root_validator(pre=True)
    def parse_body_string(data):
        if isinstance(data, str):
            return json.loads(data)
        return data

class RunResponse(BaseModel):
    rc: int = 1
    stdout: str = ""
    stderr: str = ""
    flags: Flags = Flags()
    metrics: Metrics = Metrics()

    def set_flag(self, type: str):
        if self.rc != 0:
            if type == "run":
                self.flags.run_error = True
            elif type == "build":
                self.flags.build_error = True
            elif type == "scan":
                self.flags.scan_error = True

    def set_error(self, message: str, type: str, rc: int):
        self.stderr = message
        self.rc = rc
        self.set_flag(type)
    
    def set_stdout(self, stdout):
        if len(stdout) > OUTPUT_LIMIT:
            hidden = len(stdout) - OUTPUT_LIMIT
            message = "char was" if hidden == 1 else "chars were"
            stdout = stdout[:OUTPUT_LIMIT] + (f"\n[Output truncated to {OUTPUT_LIMIT} chars, "
                                              f"{hidden} {message} hidden]")
        return stdout

    def time_limit(self, type: str, error=None):
        self.flags.timeout = True
        self.set_error("Time limit exceeded", type, 124)
    
    def memory_limit(self, type: str):
        self.flags.mem_out = True
        self.set_error("Memory limit exceeded", type, 137)

    def set_output(self, process: CompletedProcess, type: str):
        self.rc = process.returncode
        self.stderr = process.stderr
        self.stdout = self.set_stdout(process.stdout)

        self.set_flag(type)

        if self.rc == 137:
            self.memory_limit(type)
        if self.rc == 143:
            self.time_limit(type)


class Message(BaseModel):
    message_id: str
    md5_of_body: str
    body: Requests
    attributes: dict
    message_attributes: dict
    md5_of_message_attributes: str

class Details(BaseModel):
    queue_id: str
    message: Message

class MessageItem(BaseModel):
    event_metadata: dict
    details: Details

class CloudTriggerRequest(BaseModel):
    messages: List[MessageItem]