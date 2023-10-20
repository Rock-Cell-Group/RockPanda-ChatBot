from .queue import MessageQueue

POST_QUEUE = MessageQueue()  # 註冊一個推播投稿的queue，每5秒推一則，server才不會爆掉
ANSWER_QUEUE = MessageQueue()  # 註冊一個回答的queue，每5秒推一則，server才不會爆掉

__all__ = ['POST_QUEUE']