# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    PostbackAction,
    MessageAction
    # URIAction,
    # RichMenuSwitchAction,
    # CreateRichMenuAliasRequest
)

# Configure the Line Messaging API client
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Get the LINE channel access token from environment variables
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

# Configure the Line Messaging API client
configuration = Configuration(
    access_token=channel_access_token
)

# Setup line_bot_api
api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)
line_bot_blob_api = MessagingApiBlob(api_client)


# delete all existed richmenus in channel(line_bot_api)
def delete_all_existed_richmenus_in_channel():
    try:
        # 获取 richmenus 列表
        rich_menus = line_bot_api.get_rich_menu_list().richmenus
        # 建立空列表來存richmenus
        rich_menu_ids = []
        # 遍历 richmenus 列表并执行操作
        for rich_menu_response in rich_menus:
            # 获取 rich_menu_id 字段的值
            rich_menu_ids.append(rich_menu_response.rich_menu_id)

        print("Deleting all exist richmenus by rich_menu_id list below:\n", rich_menu_ids, "\n----------")
        for rich_menu_id in rich_menu_ids:
            line_bot_api.delete_rich_menu(rich_menu_id)
    except:
        return "Error"


# Define a function to create the rich menu object in JSON format
def rich_menu_object_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "rich_menu_test",
        "chatBarText": "開啟選單",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 1667, "height": 843},
                "action": {
                    "type": "postback",
                    "data": "action=fetchQuestion",
                    "inputOption": "closeRichMenu",
                    "displayText": "查詢題目"
                }
            },
            {
                "bounds": {"x": 0, "y": 843, "width": 840, "height": 843},
                "action": {
                    "type": "postback",
                    "data": "action=question_forum",
                    "inputOption": "openKeyboard",
                    "displayText": "問答專區"
                }
            },
            {
                "bounds": {"x": 840, "y": 843, "width": 840, "height": 843},
                "action": {
                    "type": "postback",
                    "data": "action=findnew_feature",
                    "inputOption": "openRichmenu",
                    #"fillInText": "看看有什麼新功能"
                }
            },
            {
                "bounds": {"x": 1667, "y": 0, "width": 833, "height": 1686},
                "action": {
                    "type": "postback",
                    "data": "action=contributeDocDB",
                    "inputOption": "closeRichMenu",
                    "displayText": "貢獻題目"
                }
            }

            # {
            # "bounds": {"x": 833, "y": 833, "width": 833, "height": 833},
            # "action": {
            # "type": "postback",
            # "data": "action=commit_post",
            # "displayText": "投稿一則快訊",
            # "inputOption": "openKeyboard",
            # "fillInText": "/!投稿\n---\n發佈者名稱: \n內容類別: \n發佈內容: \n發佈效期: \n學號: \n---"
            # }
            # },
            # {
            # "bounds": {"x": 1666, "y": 833, "width": 833, "height": 833},
            # "action": {
            # "type": "postback",
            # "data": "action=commit_feedback",
            # "displayText": "填寫反饋",
            # "inputOption": "openKeyboard",
            # "fillInText": "/!feedback\n:"
            # }
            # }
        ]
    }


# Define a function to create a Line action object based on action type
def create_action(action):
    if action['type'] == 'postback':
        return PostbackAction(
            data=action.get('data'),
            inputOption=action.get('inputOption'),
            fillInText=action.get('fillInText'),
            displayText=action.get('displayText')
        )
    elif action['type'] == 'message':
        return MessageAction(
            text=action.get('text')
        )
    else:
        return TypeError


# Main function to create and configure the rich menu
def main():
    # 2. Create rich menu object (rich_menu_test)
    rich_menu_object = rich_menu_object_json()
    areas = [
        RichMenuArea(
            bounds=RichMenuBounds(
                x=info['bounds']['x'],
                y=info['bounds']['y'],
                width=info['bounds']['width'],
                height=info['bounds']['height']
            ),
            action=create_action(info['action'])
        ) for info in rich_menu_object['areas']
    ]

    rich_menu_to_create = RichMenuRequest(
        size=RichMenuSize(width=rich_menu_object['size']['width'],
                          height=rich_menu_object['size']['height']),
        selected=rich_menu_object['selected'],
        name=rich_menu_object['name'],
        chat_bar_text=rich_menu_object['chatBarText'],
        areas=areas
    )

    # delete exist rich menus
    delete_all_existed_richmenus_in_channel()

    # create rich menu
    rich_menu_id = line_bot_api.create_rich_menu(
        rich_menu_request=rich_menu_to_create
    ).rich_menu_id
    print('Rich menu created successfully. Rich menu ID:', rich_menu_id)
    # 用絕對路徑拼接圖片路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rich_menu_data_folder_path = os.path.join(current_dir, 'richmenu_v1.png')
    with open(rich_menu_data_folder_path, 'rb') as image:
        line_bot_blob_api.set_rich_menu_image(
            rich_menu_id=rich_menu_id,
            body=bytearray(image.read()),
            _headers={'Content-Type': 'image/png'}
        )
    print('Uploading image to rich menu (Rich menu ID:', rich_menu_id, ')')

    # 6. Set rich menu A as the default rich menu
    line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_id)
    print('Setting rich menu (Rich menu ID:', rich_menu_id, ') as the default rich menu')


if __name__ == "__main__":
    main()
