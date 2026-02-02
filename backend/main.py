from fastapi import FastAPI
from utility.logger import get_logger
from routers import process_prompt


lg = get_logger(__file__)
version = "0.1.0"

app = FastAPI(
    title="PromptCrafter Backend API",
    description="API for processing and structuring prompts.",
    version=version,
)

app.include_router(process_prompt.router, prefix="/api/v1", tags=["process"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
