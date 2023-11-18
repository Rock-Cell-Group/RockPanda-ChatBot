from app.services.redis import reset_user_credits


def demo_job():
    print("demo_job run once")
    return 'demo_job run once'


def reset_user_credits_jobs():
    reset_user_credits()
    return 'reset_user_credits_jobs run once'
