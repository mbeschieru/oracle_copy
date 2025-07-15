from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.presentation.api.absence_controller import router as absence_router
from app.presentation.api.meeting_attendance_controller import (
    router as meeting_attendance_router,
)
from app.presentation.api.meeting_controller import router as meeting_router
from app.presentation.api.timesheet_controller import (
    router as timesheet_router,
)
from app.presentation.api.user_controller import router as user_router

app = FastAPI(title="Oracle Timesheet Clone")


# Add Bearer auth to OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="API for Oracle Timesheet Clone",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for op in path.values():
            op["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# Register routers
app.include_router(user_router)
app.include_router(timesheet_router)
app.include_router(absence_router)
app.include_router(meeting_router)
app.include_router(meeting_attendance_router)
