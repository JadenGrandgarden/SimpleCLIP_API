from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/ui")
async def serve_ui():
    return FileResponse('app/static/index.html')

@router.get("/test")
async def serve_test():
    return FileResponse('app/static/test.html')