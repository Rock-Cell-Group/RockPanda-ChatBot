from app.app import app
import logging

# 配置日誌記錄器
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

# 創建一個處理程序，用於將日誌消息寫入文件
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)

# 創建一個格式化程序，定義日誌消息的格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# 將處理程序添加到日誌記錄器
logger.addHandler(file_handler)


@app.get("/")
async def read_root():
    # 記錄一些日誌消息
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    return {"message": "Hello, World!"}
