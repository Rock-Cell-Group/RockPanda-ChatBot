from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.scheduler import job_service
from app.utils import MessageQueue
import pytz
import app.services.post as post_service

# Configure the scheduler
tw = pytz.timezone('Asia/Taipei')
now = datetime.now(tw)
sched = BackgroundScheduler(timezone="Asia/Taipei", daemon=True)
sched.add_job(job_service.demo_job, 'interval', minutes=1)
POST_QUEUE = MessageQueue()  # 註冊一個推播的queue，每1秒推一則，server才不會爆掉
sched.add_job(post_service.post_to_line, 'interval', seconds=1, args=[POST_QUEUE])
ANSWER_QUEUE = MessageQueue()  # 註冊一個回答的queue，每1秒推一則，server才不會爆掉 (5秒太慢)
sched.add_job(post_service.answer_to_poster, 'interval', seconds=1, args=[ANSWER_QUEUE])
sched.start()
