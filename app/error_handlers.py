from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions import AppException 
from fastapi.exceptions import RequestValidationError

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
            "code": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path),      
            "method": request.method,        
            "details": exc.details
                
            }
        }
    )
    
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload or query parameters",
                "details": exc.errors()  # Validation error Field 
            }
        }
    )
       