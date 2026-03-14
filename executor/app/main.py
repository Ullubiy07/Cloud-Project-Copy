from fastapi import FastAPI
import subprocess

from schema import Requests, RunRequest, RunResponse
from manager import FileManager, ExecManager
from config import *


app = FastAPI(
    title="Executor",
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)

def run_code(request: RunRequest):

    res = RunResponse()

    try:
        with FileManager(directory=TEST_PATH, data=res.metrics, files=request.files, language=request.language) as manager:

            with ExecManager("scan", res):
                scan_process = subprocess.run(
                    SCAN_CMD,
                    capture_output=True,
                    text=True,
                    timeout=SCAN_TIME_LIMIT,
                    cwd=manager.base_dir
                )

            if scan_process.returncode != 0:
                res.set_output(scan_process, "scan")
                return res
            
            with ExecManager("build", res):
                build_process = subprocess.run(
                    build_cmd(request.language, manager.build_stats),
                    capture_output=True,
                    text=True,
                    timeout=BUILD_TIME_LIMIT,
                    preexec_fn=set_cpu_limit,
                    cwd=manager.base_dir
                )

            if build_process.returncode != 0:
                res.set_output(build_process, "build")
                return res
            
            with ExecManager("run", res):
                run_process = subprocess.run(
                    run_cmd(request.language, manager.run_stats, request.entry_file),
                    input=request.stdin,
                    capture_output=True,
                    text=True,
                    timeout=RUN_TIME_LIMIT,
                    preexec_fn=set_cpu_limit,
                    cwd=manager.base_dir
                )

            res.set_output(run_process, "run")

    except Exception as e:
        logger.debug(e)

    return res


@app.post("/preview")
def preview(request: Requests):
    return

# WEBHOOK_URL = "https://webhook.site/1f6e6cc7-5da7-4392-9801-ec84f58d4cea"

# from fastapi import Request
# import json

@app.post("/")
def handle_cloud_trigger(request: dict):
    return "Error"
    # req = await request.body()
    # req = req.decode()

    # data = json.loads(req)

    # msg = data["messages"][0]

    # body = msg["details"]["message"]["body"]

    