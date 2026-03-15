from fastapi import FastAPI
import subprocess
import httpx

from schema import Requests, RunRequest, RunResponse, CloudTriggerRequest
from manager import FileManager, ExecManager
from config import *


app = FastAPI(
    title="Executor",
    # docs_url=None,
    # redoc_url=None,
    # openapi_url=None
)

def run_code(request: RunRequest) -> RunResponse:

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


@app.post("/")
async def handle_cloud_trigger(request: CloudTriggerRequest):
    try:
        body = request.messages[0].details.message.body

        if body.handle == "run":
            result = run_code(body.body)
            httpx.post(WEBHOOK_URL, json=result.dict())

    except Exception as e:
        logger.debug(e)

