from src.request_openai import make_completion

import logging
import os

from dotenv import load_dotenv; load_dotenv()
from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET') or 'CHANNEL_SECRETをコピペ'
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN') or 'CHANNEL_ACCESS_TOKENをコピペ'

app = FastAPI()

line_bot_api = LineBotApi(channel_access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=CHANNEL_SECRET)

logger = logging.getLogger(__name__)

@app.post("/webhook")
async def callback(request: Request):
    signature = request.headers['X-Line-Signature']
    
    body = await request.body()
    logger.info("Request body:" + body.decode())
    
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        logger.warning("Invalid signature")
        return "Invalid signature"
    
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    messages=[
    {"role": "system", "content": "You are a Qiita website engineer."},
    {"role": "user", "content": event.message.text},
    ]    
    functions=[
        {
            "name": "get_tag_info",
            "description": "Get the qiita info in a given tag",
            "parameters": {
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Tech word, e.g. Python, JavaScript, React"
                        },
                    "unit": {
                        "type": "string",
                        "enum": ["followers_count", "items_count"]
                        }
                    },
                "required": ["tag"]
                }
            }
        ] 
    reply_text = make_completion(messages, functions)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text = reply_text)
    )