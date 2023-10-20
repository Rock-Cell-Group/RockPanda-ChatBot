from fastapi import Request, HTTPException  # FastAPI
from linebot.v3.exceptions import InvalidSignatureError
from app.app import app
from app.linebot import handler
from app.utils.callback import callback_event_parser

# Handle LineBot callback requests
@app.post("/callback")
async def callback(request: Request):
    # Get the value of the X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # Get the content of the request body
    body = await request.body()

    # print("-----------------\nevent:", body.decode('utf-8'))
    # 使用者傳訊息/檔案都是從這裡印出來，
    # 如果是機器人回應訊息，會從handle_message印。
    # 目前暫時不知道點擊事件的reply_token如何傳播到下一個message event事件(可能還是要存到db裡面)
    callback_event_parser(body)

    # Handle LineBot's Webhook request
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return 'OK'
