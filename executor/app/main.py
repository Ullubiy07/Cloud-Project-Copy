from fastapi import FastAPI
import subprocess
import resource

from schema import Request, Response
from manager import FileManager, FileNameError
from config import *


app = FastAPI(
    title="Executor",
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)

def set_cpu_limit():
    resource.setrlimit(resource.RLIMIT_CPU, (TIME_LIMIT, TIME_LIMIT))


@app.post("/run", response_model=Response)
def run_code(request: Request):

    res = Response()

    try:
        with FileManager(directory=TEST_PATH, data=res.metrics, files=request.files, language=request.language) as manager:
            process = subprocess.run(
                ["/usr/bin/time", "-f", "%e %M", "-o", manager.stats,
                "timeout", "--preserve-status", f"{TIME_LIMIT}s",
                "/bin/bash", "-c", commands[request.language]],
                user="user",
                input=request.stdin,
                capture_output=True,
                text=True,
                timeout=TIME_LIMIT + 1,
                preexec_fn=set_cpu_limit,
                cwd=manager.session_dir
            )
            res.set_output(process)

    except subprocess.TimeoutExpired as e:
        res.time_limit(e)
    except FileNameError as e:
        res.set_error(str(e), 1)
    except Exception as e:
        res.set_error("Internal server error", 124)
    
    if res.rc == 137:
        res.memory_limit()
    if res.rc == 143:
        res.time_limit()

    return res
