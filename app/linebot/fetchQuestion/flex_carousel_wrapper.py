from app.services import system_file as file_service
from app.services import user as user_service
from app.services import questions as questions_service
from linebot.v3.messaging import FlexBubble

class JSON_formated_content:


    def wrapping_bubbles_in_carousel_content_list(self, question_id_list):

        all_bubbles_list = []

        for question_id in question_id_list:
            all_bubbles_list.append(
                FlexBubble.from_dict(
                    self.get_question_bubble_dict_by_question_id(question_id)
                )
            )
        return all_bubbles_list

    # generate_similar_question觸發，要把新問題包成bubble
    def get_question_bubble_dict_by_user_id(self, new_question, user_id):
        # 

        bubble = self.question_bubble_template
        bubble["header"]["contents"][0]["text"] = f'AI生成的類似題目:'
        bubble["body"]["contents"][0]["text"] = f'{new_question}'
        bubble["footer"]["contents"][0]["style"] = 'link'
        bubble["footer"]["contents"][0]["action"]["label"] = '我想複製內文'
        bubble["footer"]["contents"][0]["action"]["data"] = f'action=return_question_text@{user_id}'
        bubble["footer"]["contents"][0]["action"]["displayText"] = '我想複製內文'
        bubble["footer"]["contents"][1]["action"]["data"] = f'action=answer_to_AI_question@{user_id}'

        return bubble


    # 選完三個選項的最後一個時自動觸發。
    def get_question_bubble_dict_by_question_id(self, question_id):
        # 
        file_id = questions_service.get_column_value_by_question_id(question_id, "file_id")
        number_in_file = questions_service.get_column_value_by_question_id(question_id, "number_in_file")
        question_raw_text = questions_service.get_column_value_by_question_id(question_id, "raw_text")

        bubble = self.question_bubble_template
        bubble["header"]["contents"][0]["text"] = f'考卷{file_id}的第{number_in_file}題:'
        bubble["body"]["contents"][0]["text"] = f'{question_raw_text}'
        bubble["footer"]["contents"][0]["action"]["data"] = f'action=generate_similar_question@{question_id}' # TODO USER table要存使用者上次生成的內容，這樣才能一直迴圈產生新的類似的，不然都based on固定的question_id可能按下生成類似好幾次都一樣
        bubble["footer"]["contents"][1]["action"]["data"] = f'action=answer_to_db_question@{question_id}'

        return bubble


    # 還有個hero區塊沒用到
    question_bubble_template = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "file_id & number_in_file"
            }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "background": {
            "type": "linearGradient",
            "angle": "45deg",
            "startColor": "#E3E4FA",
            "endColor": "#C9DFEC"
            },
            "contents": [
            {
                "type": "text",
                "text": "raw_text",
                "wrap": True
            }
            ]
        },
        "footer":{
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "生成類似考題",
                        "data": "action=generate@",
                        "displayText": "生成類似考題",
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "請問此題詳解(beta)",
                        "data": "action=answer@",
                        "displayText": "請問此題詳解(beta)",
                    }
                }
            ],
        }
    }












'''
{
  "type": "template",
  "altText": "this is a carousel template",
  "template": {
    "type": "carousel",
    "columns": [
      {
        "thumbnailImageUrl": "https://example.com/bot/images/item1.jpg",
        "imageBackgroundColor": "#FFFFFF",
        "title": "this is menu",
        "text": "description",
        "defaultAction": {
          "type": "uri",
          "label": "View detail",
          "uri": "http://example.com/page/123"
        },
        "actions": [
          {
            "type": "postback",
            "label": "Buy",
            "data": "action=buy&itemid=111"
          },
          {
            "type": "postback",
            "label": "Add to cart",
            "data": "action=add&itemid=111"
          },
          {
            "type": "uri",
            "label": "View detail",
            "uri": "http://example.com/page/111"
          }
        ]
      },
      {
        "thumbnailImageUrl": "https://example.com/bot/images/item2.jpg",
        "imageBackgroundColor": "#000000",
        "title": "this is menu",
        "text": "description",
        "defaultAction": {
          "type": "uri",
          "label": "View detail",
          "uri": "http://example.com/page/222"
        },
        "actions": [
          {
            "type": "postback",
            "label": "Buy",
            "data": "action=buy&itemid=222"
          },
          {
            "type": "postback",
            "label": "Add to cart",
            "data": "action=add&itemid=222"
          },
          {
            "type": "uri",
            "label": "View detail",
            "uri": "http://example.com/page/222"
          }
        ]
      }
    ],
    "imageAspectRatio": "rectangle",
    "imageSize": "cover"
  }
}

'''