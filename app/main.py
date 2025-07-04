from fastapi import FastAPI,Depends
from app.presentation.api.user_controller import router as user_router
from app.presentation.api.timesheet_controller import router as timesheet_router
from app.presentation.dependencies.header_user import get_authenticated_user_id

app = FastAPI(title="Oracle Timesheet Clone",
              dependencies=[Depends(get_authenticated_user_id)])

# Register routers
app.include_router(user_router)
app.include_router(timesheet_router)
