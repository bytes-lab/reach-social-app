from django.core.mail import EmailMessage
from django.template.loader import get_template


import uuid
import os


def get_file_path(instance, filename):
    """
    Upload images
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(instance.__class__.__name__.lower(), filename)


def send_email(subject, content):
    to = []  # TODO change email to admin
    from_email = 'ufeed.ru@gmail.com'
    ctx = {
        'content': content,
    }
    message = get_template('report_email.html').render(ctx)
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
