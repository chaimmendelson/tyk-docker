from fastapi import FastAPI, Request
from typing import Dict
import uvicorn

app = FastAPI(
    version="1.0.0",
)

app.openapi_version = "3.0.3"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def echo(path: str, request: Request) -> Dict:
    return {
        "method": request.method,
        "url": str(request.url),
        "host": request.client.host,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
        "cookies": request.cookies,
        "body": (await request.body()).decode("utf-8") if await request.body() else None,
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
