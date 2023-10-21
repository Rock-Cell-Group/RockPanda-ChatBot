from linebot.v3.webhooks import MessageEvent, TextMessageContent, FileMessageContent
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, ReplyMessageRequest, TextMessage


# lineBot訊息處理器
async def handle_message(event, line_bot_api):
    print(f"{event}")

    # 開始處理訊息內容

    # Get the user's message
    user_message = event.message.text

    # 初始化cmd為null
    cmd = None
    if '/' in user_message:
        split_lines = user_message.splitlines()
        if len(split_lines) > 1:
            cmd = split_lines[0]
            # user_message_content = "\n".join(split_lines[1:])
        else:
            await line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="格式有誤請重新點選！")]
                )
            )

    # 我們定義的行為'/!'
    if cmd == "/!快速發問":
        print(f"來自{event.source.user_id}的快速發問處理中")
        event.message.text = "\n".join(user_message.split("\n")[1:])
        if len(event.message.text) < 15:
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="字數太少囉")]
                )
            )
        else:
            print(f"來自{1}的提問，已儲存至id：{1}")
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="已將您的提問發布於問答平台上！")]
                )
            )

    return 'OK'
