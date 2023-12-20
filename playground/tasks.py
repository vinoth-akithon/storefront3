from time import sleep
from celery import shared_task


@shared_task
def long_running_task():
    print("Long Running Task Started")
    sleep(10)
    print("Long Running Task Ended")
