from fastapi import FastAPI
from app.presentation.api.user_controller import router as user_router
from app.presentation.api.timesheet_controller import router as timesheet_router

app = FastAPI(title="Oracle Timesheet Clone")

# Register routers
app.include_router(user_router)
app.include_router(timesheet_router)
