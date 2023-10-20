from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration
from app.config import settings

# setup LineBot with related secret key
configuration = Configuration(access_token=settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)
