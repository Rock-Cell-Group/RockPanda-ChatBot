import json
import uuid
from contextlib import contextmanager

from app.model import models
from app.model.database import SessionLocal


# Function to get the database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def callback_event_parser(body):
    # print("callback_event_parser")
    try:
        # Decode the bytes and parse JSON
        json_data = json.loads(body.decode('utf-8'))

        # 如果callback event是message，不是postback, join, unrend, follow之類的https://developers.line.biz/en/docs/messaging-api/receiving-messages/#webhook-event-in-one-on-one-talk-or-group-chat
        # 那就會insert callback event to db
        event = json_data['events'][0]
        callback_event_type = event.get('type', {})
        if callback_event_type == 'message':
            print("\n-----callback event是message, 開始將對話或檔案存進db-----\n")

            # initialize Dialogue object
            dialogue = models.Dialogue()
            dialogue.dialogue_type = "callback"


            message = event.get('message', {})
            source = event.get('source', {})
            content_provider = message.get('contentProvider', {})

            dialogue.dialogue_destination = json_data.get('destination', '')
            dialogue.event_type = event.get('type', '')
            dialogue.event_webhook_event_id = event.get('webhookEventId', '')
            # dialogue.event_delivery_context = event.get('deliveryContext', '')  # deprecated
            dialogue.event_timestamp = event.get('timestamp', '')
            dialogue.event_source_type = source.get('type', '')
            dialogue.event_source_user_id = source.get('userId', '')
            dialogue.event_reply_token = event.get('replyToken', '')
            dialogue.event_mode = event.get('mode', '')
            dialogue.message_type = message.get('type', '')
            dialogue.message_id = message.get('id', '')
            dialogue.message_quote_token = message.get('quoteToken', '')
            dialogue.message_text = message.get('text', '')
            dialogue.message_sticker_id = message.get('stickerId', '')
            dialogue.message_package_id = message.get('packageId', '')
            dialogue.message_sticker_resource_type = message.get('stickerResourceType', '')
            dialogue.message_content_provider_type = content_provider.get('type', '')
            dialogue.message_file_name = message.get('fileName', '')
            dialogue.message_file_size = message.get('fileSize', '')
            dialogue.message_file_extension = message.get('fileName', '').split(".")[-1]
            dialogue.message_file_content_provider_type = content_provider.get('type', '')
            dialogue.message_emojis = message.get('emojis', '')
            dialogue.message_mention = message.get('mention', '')
            dialogue.message_quoted_message_id = message.get('quotedMessageId', '')
            # TODO 整合
            with get_db() as db:
                # if message['type'] in ['file']:
                

                #     # 這裡要把檔案路徑存到db
                #     file = models.FileSystem()
                #     file.user_id = dialogue.event_source_user_id
                #     file.file_path = file_path
                #     file.file_name = dialogue.message_file_name
                #     file.file_extension = dialogue.message_file_extension
                #     file.file_size = dialogue.message_file_size

                #     # insert file to db
                #     db.add(file)
                #     db.commit()
                #     db.refresh(file)
                #     dialogue.file_id = file.id

                # insert dialogue to db
                db.add(dialogue)
                db.commit()
                db.refresh(dialogue)

            # print("callback_event_parser end")
            return dialogue

    except Exception as e:
        print(f"Error in callback_event_parser: {e}")
        return None


def file_fetcher(dialogue):
    """
    # API文件寫法
    # GET https://api-data.line.me/v2/bot/message/{messageId}/content
    #
    # curl -v -X GET https://api-data.line.me/v2/bot/message/{messageId}/content \
    # -H 'Authorization: Bearer {channel access token}'
    """

    import requests
    from dotenv import load_dotenv
    from os import environ

    load_dotenv()
    channel_access_token = environ.get("CHANNEL_ACCESS_TOKEN")

    url = f"https://api-data.line.me/v2/bot/message/{dialogue.message_id}/content"
    headers = {
        "Authorization": f"Bearer {channel_access_token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_path = f"./data/Upload_Data/{uuid.uuid4()}.{dialogue.message_file_extension}"
        with open(file_path, "wb") as f:
            f.write(response.content)
            return file_path

    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Response content: {response.text}")

    return None


# callback接收文字訊息
# {
#     "destination": "U118e7ba623b02c637673384930dc0035",
#     "events": [
#         {"type": "message",
#          "message": {
#              "type": "text",
#              "id": "476354485175451954",
#              "quoteToken": "mi9U-tiJPksyQOXeAiRZTtRmMKd6mdJ3qbPxx7qCfvxBWUiaYmpfnBzDy7TUPnzbiKSIlGdbT_7L1kkKxx8wJIELpFR6iisLdhsQyIQhGd4Qecau-6zzC7yIL73Sx1Ct0VfzHKqc5qsPE_yyrX1ogw",
#              "text": "sad"},
#          "webhookEventId": "01HC7D3ADBCXZMD5GZMVTYCPAJ",
#          "deliveryContext": {"isRedelivery": false},
#          "timestamp": 1696760702895,
#          "source": {"type": "user", "userId": "U4df6a2535fcae2dc9277c39aec86ca66"},
#          "replyToken": "73718db268194b018f37d74f60da1754", "mode": "active"
#          }
#     ]
# }


# callback接收貼圖
# {"destination": "U118e7ba623b02c637673384930dc0035",
#  "events": [
#      {"type": "message",
#       "message": {"type": "sticker",
#                   "id": "476355763867222274",
#                   "quoteToken": "G2NZCgNRGjYfhWEDr6xaIDkT4i_laFwe_0qd6_L2WXplV2eeGVRgUUN7btDJZu3C5921gp2WKcsrY6Nu_gUvlYCn0oftQ_qMUkrsUqodKxpTkRsNg_yjNWo-MeTm6gjXVHCZdO6WTGqjssJ-zdg_Kg",
#                   "stickerId": "32809036",
#                   "packageId": "3128490",
#                   "stickerResourceType": "STATIC"},
#       "webhookEventId": "01HC7DTJKAJD0H8Y4T203Y1EGT",
#       "deliveryContext": {"isRedelivery": false},
#       "timestamp": 1696761464936,
#       "source": {"type": "user",
#                  "userId": "U4df6a2535fcae2dc9277c39aec86ca66"},
#       "replyToken": "89335a31b7da45eeb7d8f98611b71e48",
#       "mode": "active"}]}


# callback接收圖片訊息
# {"destination": "U118e7ba623b02c637673384930dc0035",
#  "events": [{
#      "type": "message",
#      "message": {"type": "image",
#                  "id": "476356038325961013",
#                  "quoteToken": "fJuU-aFNeuhI0zztnq759rs_CvIZXlZ_Kwpc9OF8Je6we6M6Z9j4AkC0p2FosHHRAsWCw1W0YOOGaQYj-SNZA4QYLuK2FKNwrHlRmGsEGJjUBbe10NoN2_YZBhcZFVb4SsKfDWhuvQCu9W9JKAgLdw",
#                  "contentProvider": {
#                      "type": "line"}},
#      "webhookEventId": "01HC7DZK4RWWTX1T3F0TRF8QCP",
#      "deliveryContext": {"isRedelivery": false},
#      "timestamp": 1696761629573, "source": {"type": "user",
#                                             "userId": "U4df6a2535fcae2dc9277c39aec86ca66"},
#      "replyToken": "d87bb3266cfe45819bfbbbdc78800462",
#      "mode": "active"}]}


# callback接收檔案訊息
# {"destination": "U118e7ba623b02c637673384930dc0035",
#  "events": [{"type": "message",
#              "message": {"type": "file", "id": "476356638547116520",
#                          "fileName": "493563768(2).pdf",
#                          "fileSize": 481971,
#                          "contentProvider": {"type": "line"}},
#              "webhookEventId": "01HC7EAFQS33Q76AA54SG8DM99",
#              "deliveryContext": {"isRedelivery": false},
#              "timestamp": 1696761986422, "source": {"type": "user",
#                                                     "userId": "U4df6a2535fcae2dc9277c39aec86ca66"},
#              "replyToken": "a3f6f7b818864ba988d1b9deadcafca0",
#              "mode": "active"}]}
