
import logging

from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from hc.celery import app
from hc.front.models import EmailTasks


@app.task 
def send_scheduled_mail():
    mail_tasks = EmailTasks.objects.all()
    if not mail_tasks:
        return "no scheduled tasks"
    for mail_task in mail_tasks:
        send_mail(
            mail_task.subject,
            get_template('emails/email-tasks-html.html').render(
                Context({
                    'message':mail_task.message,
                    'owner':mail_task.owner,
                })
            ),
            'hcrogueone@gmail.com',
            [mail_task.recipients],
            fail_silently=False,
        )


