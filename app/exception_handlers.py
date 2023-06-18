from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

REQUEST_VALIDATION_ERROR_STATUS = 422
ENTITY_ERROR_STATUS = 400


def validation_handler(request, exc):
    return JSONResponse(status_code=REQUEST_VALIDATION_ERROR_STATUS,
                        content={'status': 'error', 'message': exc.errors()[0]['msg']})


def unique_vailation_handler(request, exc):
    if 'errors.UniqueViolation' in str(exc):
        return JSONResponse(status_code=ENTITY_ERROR_STATUS,
                            content={'status': 'error', 'message': 'Duplicate unique property detected'})
    else:
        raise HTTPException(status_code=500, detail="Internal server error")


def entity_error_handler(request, exc):
    return JSONResponse(status_code=ENTITY_ERROR_STATUS, content={'status': 'error', 'message': str(exc)})
