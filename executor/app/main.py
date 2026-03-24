from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import httpx

from schemas.cloud import Requests, CloudTriggerRequest
from routers.execute import run_code
from config.config import env, logger


app = FastAPI(
    title="Executor"
)


@app.post("/preview")
def preview(request: Requests):
    return


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logger.debug(f"422 Validation Error: {exc_str}")
    logger.debug(f"Content that caused error: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.post("/")
def handle_cloud_trigger(request: CloudTriggerRequest):
    try:
        body = request.messages[0].details.message.body

        if body.handle == "run":
            res = run_code(body.body)
            httpx.post(env.WEBHOOK_URL, json=res.dict())
        
        if body.handle == "debug":
            return

    except Exception as e:
        logger.debug(e)

