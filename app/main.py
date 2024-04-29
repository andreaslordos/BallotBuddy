import os
from fastapi import FastAPI, Form, Response, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from api import getReply

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello, world."}

@app.post("/hook")
async def chat(
    request: Request, From: str = Form(...), Body: str = Form(...) 
):
    validator = RequestValidator(os.environ["TWILIO_AUTH_TOKEN"])
    form_ = await request.form()
    if not validator.validate(
        str(request.url), 
        form_, 
        request.headers.get("X-Twilio-Signature", "")
    ):
        raise HTTPException(status_code=400, detail="Error in Twilio Signature")
    
    reply = getReply(From, Body)[0]
    print("Received reply:", reply)
    response = MessagingResponse()
    msg = response.message(reply)
    return Response(content=str(response), media_type="application/xml")