from fastapi import Request
import time
import json
from functools import wraps

from dependency_injector.wiring import inject as di_inject
from loguru import logger

from app.services.weavite__service import BaseService


def inject(func):
    @di_inject
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Injecting dependencies into {func.__name__}")
        result = func(*args, **kwargs)
        injected_services = [arg for arg in kwargs.values() if isinstance(arg, BaseService)]
        if len(injected_services) == 0:
            return result
        else:
            try:
                injected_services[-1].close_scoped_session()
            except Exception as e:
                logger.error(e)

        return result

    return wrapper


async def request_debug_middleware(request: Request, call_next):
    """Middleware to log request details"""
    print(f"\n=== REQUEST: {request.method} {request.url.path} ===")
    
    # Try to log body for POST/PUT requests
    if request.method in ["POST", "PUT"]:
        try:
            # For multipart form data
            if "multipart/form-data" in request.headers.get("content-type", ""):
                form = await request.form()
                print(f"Form data keys: {list(form.keys())}")
                for key in form.keys():
                    if hasattr(form[key], "filename"):
                        print(f"File field '{key}': filename={form[key].filename}")
                    else:
                        print(f"Form field '{key}': {form[key]}")
        except Exception as e:
            print(f"Error parsing request body: {str(e)}")
    
    # Process the request and time it
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"Status code: {response.status_code}")
    print(f"Process time: {process_time:.4f} seconds")
    print(f"=== END REQUEST ===\n")
    
    return response