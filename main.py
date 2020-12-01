import os
from os import name
from typing import Any, List, Optional
from fastapi import FastAPI, Request
from fastapi.params import Header
from fastapi.staticfiles import StaticFiles
from linebot.models.send_messages import ImageSendMessage
from pydantic import BaseModel
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage
from qrcode import QRCode
import qrcode
import random

URL = os.environ['URL']


class RequestBody(BaseModel):
    events: Optional[List[Any]]
    destination: str


app = FastAPI()
line_bot = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINE_SECRET'])

app.mount("/qrcodes", StaticFiles(directory="qrcodes"), name="static")


@app.get("/")
async def get_root():
    return "OK"


@app.post("/webhook")
async def post_webhook(request_body: Request, X_Line_Signature: str = Header(None)):
    body = await request_body.body()
    handler.handle(body.decode(), X_Line_Signature)
    return {"detail": "OK"}


@handler.add(MessageEvent, message=TextMessage)
def handle_text(event):
    code = qrcode.make(event.message.text)
    fname = "qrcodes/qrcodes"+str(random.randint(100000, 1000000))
    code.save(fname)
    line_bot.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url=URL+fname,
            preview_image_url=URL+fname
        )
    )
