from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from .tasks import send_report

def init_scheduler(app):
    scheduler = BackgroundScheduler(timezone=app.config['TIMEZONE'])
    scheduler.add_job(func=lambda: run_send_report(app),
                      trigger='cron',
                      hour=16, minute=0)
    scheduler.start()
    app.logger.info("Scheduler khởi chạy: gửi báo cáo mỗi ngày 16:00")

def run_send_report(app):
    with app.app_context():
        send_report()