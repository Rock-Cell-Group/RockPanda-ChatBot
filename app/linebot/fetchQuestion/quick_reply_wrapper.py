# quick_reply_module.py
# usage example:
# from quick_reply_module import quickReply_1, quickReply_2

import app.services.system_file as file_service
from app.model import models
from typing import List, Tuple, Type


class JSON_formated_content:


    # 如果question_course有任何一筆是空的就會error
    def get_course_quick_reply_dict(model_class: Type[models.FileSystem], column_name: str):
        # 假设你有一个课程名称列表
        courses = file_service.get_column_value_set(models.FileSystem, column_name)

        quickReply = {
            "type": "text",
            "text": "請從以下資料庫有的科目範圍選擇科目!",
            "quickReply": {
                "items": []
            }
        }

        # 使用循环遍历课程名称列表，为每个课程生成一个 quickReply item
        # TODO 限制最多增加到13個item，這是LINE quickReply的規格限制。
        for course_name in courses:
            if course_name:
                item = {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": course_name,
                        "data": f"action=select_course@{course_name}",
                        "displayText": f"選擇{course_name}"
                    }
                }
                # 将生成的 item 添加到 quickReply 的 items 列表中
                quickReply["quickReply"]["items"].append(item)

        # 输出生成的 quickReply JSON
        return quickReply
    

    def get_quick_reply_dict_by_former(model_class: Type[models.FileSystem], conditions: List[Tuple[str, str]], column2_name: str) -> dict:
        
        # 調用get_column_value_set_by_conditions函數來獲取列值列表
        gotcolumn_list = file_service.get_column_value_set_by_conditions(model_class, conditions, column2_name)
        en2ch = {"question_professor": "授課老師", "question_exam_type": "期中/期末"}

        # 初始化一个空的 quickReply
        quickReply = {
            "type": "text",
            "text": f"請選擇{en2ch[column2_name]}:",
            "quickReply": {
                "items": []
            }
        }

        # 使用循环遍历课程名称列表，为每个课程生成一个 quickReply item
        # TODO 限制最多增加到13個item，這是LINE quickReply的規格限制。
        for gotcolumn_value in gotcolumn_list:
            if gotcolumn_value:
                item = {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": gotcolumn_value,
                        "data": f"action=select_{column2_name}@{gotcolumn_value}",
                        "displayText": f"選擇{gotcolumn_value}"
                    }
                }
                # 将生成的 item 添加到 quickReply 的 items 列表中
                quickReply["quickReply"]["items"].append(item)

        # 输出生成的 quickReply JSON
        return quickReply 
        
  
    #目前沒用到被上面那個get_course_quick_reply_dict取代了，會自動填充科目。
    quickReply_1 = {
        "type": "text",
        "text": "請從以下資料庫有的科目範圍選擇科目!",
        "quickReply": {
            "items": [
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "分子細胞生物學二",
                        "data": "action=select_subject@1",
                        "displayText": "選擇分子細胞生物學二"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "分子細胞生物學三",
                        "data": "action=select_subject@2",
                        "displayText": "選擇分子細胞生物學三"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "生物物理化學",
                        "data": "action=select_subject@3",
                        "displayText": "選擇生物物理化學"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "生物發育學",
                        "data": "action=select_subject@4",
                        "displayText": "選擇生物發育學"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "微生物學",
                        "data": "action=select_subject@5",
                        "displayText": "選擇微生物學"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "遺傳學",
                        "data": "action=select_subject@6",
                        "displayText": "選擇遺傳學"
                    }
                }
            ]
        }
    }

    #目前沒用到被上面那個get_quick_reply_dict_by_former取代了，會自動填充老師。
    quickReply_2 = {
        "type": "text",
        "text": "請從下方老師中選擇想要出題的",
        "quickReply": {
            "items": [
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "不選擇特定老師",
                        "data": "action=select_teacher@0",
                        "displayText": "不選擇特定老師"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "聘任中1",
                        "data": "action=select_teacher@1",
                        "displayText": "選擇聘任中1"
                    }
                },
                {
                    "type": "action",
                    "action": {
                        "type": "postback",
                        "label": "聘任中2",
                        "data": "action=select_teacher@2",
                        "displayText": "選擇聘任中2"
                    }
                }
            ]
        }
    }