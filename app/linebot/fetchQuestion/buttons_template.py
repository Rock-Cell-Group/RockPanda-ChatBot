class JSON_formated_content:
    bottoms_1 = {
        "type": "template",
        "altText": "This is a buttons template",
        "template": {
            "type": "buttons",
            "text": "請選擇要進入哪一種模式\n  ◎選項式:會透過選項調用資料庫中的特定題目\n  ◎指令式:會由大語言模型判斷你需要哪些題目",
            "actions": [
            {
                "type": "postback",
                "label": "選項式",
                "data": "action=fetchQuestionbyOption",
                "displayText": "選擇選項式"
            },
            {
                "type": "postback",
                "label": "指令式",
                "data": "action=fetchQuestionbyMassage",
                "displayText": "選擇指令式",
                "inputOption": "openKeyboard",
                "fillInText": "請幫我"
            }
            ]
        }
    }


    bottoms_2 = {
        "type": "template",
        "altText": "This is a buttons template",
        "template": {
            "type": "buttons",
            "text": "請選擇要上傳文件還是查詢先前上傳結果",
            "actions": [
            {
                "type": "postback",
                "label": "上傳文件",
                "data": "action=uploadDocument",
                "displayText": "上傳文件",
                "inputOption": "openKeyboard",
                "fillInText": "/Document_information\n課程=\n授課老師=\n類型="
            },
            {
                "type": "postback",
                "label": "查詢先前上傳結果",
                "data": "action=checkUploadStatus",
                "displayText": "查詢先前上傳結果"
            }
            ]
        }
    }




'''
line 官方範例:https://developers.line.biz/en/reference/messaging-api/#template-messages
{
  "type": "template",
  "altText": "this is a confirm template",
  "template": {
    "type": "confirm",
    "text": "Are you sure?",
    "actions": [
      {
        "type": "message",
        "label": "Yes",
        "text": "yes"
      },
      {
        "type": "message",
        "label": "No",
        "text": "no"
      }
    ]
  }
}
'''