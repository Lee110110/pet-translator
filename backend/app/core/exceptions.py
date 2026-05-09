from fastapi import Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, message: str = "资源不存在"):
        self.message = message


class ConflictError(Exception):
    def __init__(self, message: str = "资源冲突"):
        self.message = message


class ForbiddenError(Exception):
    def __init__(self, message: str = "无权访问"):
        self.message = message


async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"detail": exc.message})