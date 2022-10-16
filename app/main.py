from fastapi import FastAPI, Request, Response, Cookie, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Union
import uuid


########################################################
### GLOBAL in memory session state
### depends on concurrency of 1. only useful for very simple test env to cheap out on state.
### Note: Do this with a simple redis instance if things get more complex.

sessions = {}

########################################################
### APP

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

########################################################
### ROUTES


@app.get("/", response_class=HTMLResponse)
async def read_item(
    request: Request, svt_session: Union[str, None] = Cookie(default=None)
):
    global sessions
    csrf_token = str(uuid.uuid4())[:8]
    session_valid = svt_session in sessions
    if session_valid:
        sessions[svt_session]["csrf_token"] = csrf_token

    return templates.TemplateResponse(
        "root.jinja",
        {
            "request": request,
            "svt_session": svt_session,
            "session_valid": session_valid,
            "csrf_token": csrf_token,
        },
    )


@app.get("/debug")
def del_session(request: Request):
    global sessions
    return {"sessions": sessions, "cookies": request.cookies}


@app.post("/login")
def create_session(request: Request, response_class=HTMLResponse):
    global sessions
    session_uuid = str(uuid.uuid4())

    # cheap solotion for global session state in memory
    sessions[session_uuid] = {"valid": 1}

    response = templates.TemplateResponse("login.jinja", {"request": request})
    response.set_cookie(key="svt_session", value=session_uuid)
    return response


@app.post("/logout")
def del_session(request: Request, response_class=HTMLResponse):
    response = templates.TemplateResponse("logout.jinja", {"request": request})
    response.delete_cookie("svt_session")
    return response


@app.post("/step2", response_class=HTMLResponse)
async def read_item(
    request: Request,
    csrf_token: str = Form(None),
    input1: str = Form(None),
    svt_session: Union[str, None] = Cookie(default=None),
):
    global sessions
    success = 0;
    if svt_session:
        if svt_session in sessions:
            if "csrf_token" in sessions[svt_session]:
                if csrf_token:
                    if sessions[svt_session]["csrf_token"] == csrf_token:
                        status = "SUCCESS!"
                        success = 1
                    else:
                        status = "FAILURE: csrf_token passed, but incorrect"
                else:
                    status = "FAILURE: No csrf_token passed"
            else:
                status = "FAILURE: Somehow, svt_session on server has no csrf_token set. Did you even visit the form?"
        else:
            status = "FAILURE: svt_session cookie is stale"
    else:
        status = "FAILURE: No svt_session cookie was sent"

    return templates.TemplateResponse(
        "step2.jinja",
        {"request": request, "status": status, "success": success, "input1": input1},
    )
