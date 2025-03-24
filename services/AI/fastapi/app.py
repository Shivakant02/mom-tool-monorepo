import uvicorn
from fastapi import FastAPI
from modules.meeting import meeting_router
from modules.teams_chat import teams_router
from modules.send_mail import mail_router
from modules.fixing_names import fixing_router

app = FastAPI()

app.include_router(meeting_router, prefix="/api")
app.include_router(teams_router, prefix="/api")
app.include_router(mail_router, prefix="/api")
app.include_router(fixing_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
