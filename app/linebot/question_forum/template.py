class JSON_formated_content:

    def get_open_question_bubble_dict(
            self,
            question_categrory,
            question_content,
            question_post_time,
            question_id):
        bubble = self.open_question_bubble_template
        bubble["body"]["contents"][0]["text"] = f'{question_categrory} '  # 故意加個空格，才不會沒填的時候被line擋住
        bubble["body"]["contents"][1]["text"] = f'{question_content} '  # 故意加個空格，才不會沒填的時候被line擋住
        bubble["body"]["contents"][2]["text"] = question_post_time
        bubble["body"]["contents"][1]["action"]["data"] = f'action=show_all_text&question_id={question_id}'
        bubble["footer"]["contents"][0]["action"]["fillInText"] = f'/!我來回答\n問題編號：{question_id}\n建議答案：'
        return bubble

    def get_my_question_bubble_dict(
            self,
            question_categrory,
            question_content,
            question_post_time,
            question_id):
        bubble = self.my_question_bubble_template
        bubble["body"]["contents"][0]["text"] = f'{question_categrory} '  # 故意加個空格，才不會沒填的時候被line擋住
        bubble["body"]["contents"][1]["text"] = f'{question_content} '  # 故意加個空格，才不會沒填的時候被line擋住
        bubble["body"]["contents"][2]["text"] = question_post_time
        bubble["body"]["contents"][1]["action"]["data"] = f'action=show_all_text&question_id={question_id}'
        bubble["footer"]["contents"][0]["action"]["data"] = "action=delete_question&question_id=" + question_id
        return bubble

    bottoms_1 = {
        "type": "template",
        "altText": "This is a buttons template",
        "template": {
            "type": "buttons",
            "text": "請選擇要查看的對象\n  ◎我是學霸：幫其他使用者解惑\n  ◎我是學渣：查看個人歷史提問",
            "actions": [
                {
                    "type": "postback",
                    "label": "快速發問",
                    "data": "action=create_question",
                    "displayText": "快速發問",
                    "inputOption": "openKeyboard",
                    "fillInText": '/!快速發問\n領域：\n問題：'
                },
                {
                    "type": "postback",
                    "label": "我是學渣",
                    "data": "action=list_my_question",
                    "displayText": "我是學渣"
                },
                {
                    "type": "postback",
                    "label": "我是學霸",
                    "data": "action=list_all_question",
                    "displayText": "我是學霸"
                }
            ]
        }
    }

    open_question_bubble_template = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "",
                    "weight": "bold",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "",
                    "weight": "regular",
                    "size": "sm",
                    "action": {
                        "type": "postback",
                        "label": "查看全文",
                        "data": "action=show_all_text&question_id=",
                        "displayText": "查看全文"
                    },
                    "wrap": True,
                    "align": "start"
                },
                {
                    "type": "text",
                    "text": "",
                    "size": "sm",
                    "align": "end",
                    "offsetTop": "md"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "我來回答",
                        "data": "action=response_question",
                        "displayText": "我來回答",
                        "inputOption": "openKeyboard",
                        "fillInText": '/!我來回答\n問題編號：\n建議答案：'
                    }
                },
                # {
                #     "type": "button",
                #     "style": "link",
                #     "height": "sm",
                #     "action": {
                #         "type": "postback",
                #         "label": "我來回答2",
                #         "data": "action=response_question",
                #         "displayText": "我來回答2",
                #         "inputOption": "openKeyboard",
                #         "fillInText": '/!我來回答\n問題編號：\n建議答案：'
                #     }
                # },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }

    my_question_bubble_template = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "【機器學習】",
                    "weight": "bold",
                    "align": "center"
                },
                {
                    "type": "text",
                    "text": "",
                    "weight": "regular",
                    "size": "sm",
                    "action": {
                        "type": "postback",
                        "label": "查看全文",
                        "data": "action=show_all_text&question_id=",
                        "displayText": "查看全文"
                    },
                    "wrap": True,
                    "align": "start"
                },
                {
                    "type": "text",
                    "text": "發佈時間：2023/10/14",
                    "size": "sm",
                    "align": "end",
                    "offsetTop": "md"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "data": "action=delete_question",
                        "label": "刪除提問"
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
            ],
            "flex": 0
        }
    }
