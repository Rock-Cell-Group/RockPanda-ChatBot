import os
import traceback
import app.router.user as user_router
import pytz
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.model import models
from app.model.database import engine
from app.scheduler.job_service import demo_job
from app.utils.csv_parser import parse_file_system_csv_to_db, parse_question_csv_to_db
from richmenu import setup_richmenu

# orm自動建表 (註解掉，一律由聖凱手動建表，因為planetscale會擋DDL操作)
if settings.CONFIG_TYPE == "BaseConfig":  # 只有在local db才建表
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="chatbot API Docs",
    description="FastAPI chatbot",
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redocs',
    swagger_ui_parameters={"defaultModelsExpandDepth": -1})
# app: FastAPI = FastAPI(servers=[{'url': 'http://localhost:8000'}])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_status = {}


@app.get('/demo-job')
def job1():
    return demo_job()


@app.on_event("startup")
async def startup_event():
    with open("serverLog.txt", mode="a") as log:
        log.write("Application startup at " + str(datetime.now(pytz.timezone("Asia/Taipei"))) + " \n")

    # Step1: Create rich menu
    try:
        setup_richmenu.main()
        print("rich menu created")
    except Exception as e:
        print(traceback.print_exc())

    # Step2: check DB connection and insert initial data
    try:
        engine = create_engine(
            f'{settings.DATABASE_URL}')
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        # 塞入初始資料(題目們)
        # Explicitly declare the SQL query as a text object
        query = text("SELECT count(*) FROM `RAG_FILE_SYSTEM`")
        db_file_number = db.execute(query).scalar()
        if db_file_number == 0:  # 絕對路徑寫法比較安全，但是container內的folder名稱必須叫RAG_ChatBot，不能換名字
            print('DB is empty, start to insert initial data')
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            file_system_data_folder_path = os.path.join(parent_dir, 'data/Question_Data/rag_file_system.csv')
            parse_file_system_csv_to_db(file_system_data_folder_path)
            question_data_folder_path = os.path.join(parent_dir, 'data/Question_Data/rag_questions.csv')
            parse_question_csv_to_db(question_data_folder_path)
            print('Initial data inserted successfully')

    # step3: ...
    # step4: ...
    # step5: ...

    except Exception as e:
        print(traceback.print_exc())


@app.on_event("shutdown")
def shutdown_event():
    with open("serverLog.txt", mode="a") as log:
        log.write("Application shutdown at " + str(datetime.now(pytz.timezone("Asia/Taipei"))) + " \n")


# Define the root route, returning "LineBot is running."
@app.get('/')
def hello_world():
    return 'LineBot is running.'


app.include_router(user_router.router)

# Import the modules containing the handlers for each event type
# the handlers for each event type in __init__.py will be imported and initialized
from app.linebot import (
    callback,
    follow_event,
    message_event,
    postback_event
)

# If this is the main program, run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    # Run the application on host "0.0.0.0" and port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
