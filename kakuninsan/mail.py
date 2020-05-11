import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from jinja2 import Environment, FileSystemLoader
import base64


class Mail:
    def __init__(self, smtp_dict):
        self.smtp_dict = smtp_dict.copy()

    def create_message(self, body_dict):
        msg = MIMEText(body_dict['body'], 'html')
        msg['Subject'] = body_dict['subject']
        msg['To'] = self.smtp_dict['mail_to']
        msg['Date'] = formatdate()
        return msg

    def send_mail(self, msg):
        smtp_obj = smtplib.SMTP(self.smtp_dict['smtp_server'], self.smtp_dict['smtp_port'])
        try:
            smtp_obj.ehlo()
            smtp_obj.starttls()
            smtp_obj.login(self.smtp_dict['smtp_user'], self.smtp_dict['smtp_pass'])
            smtp_obj.sendmail(self.smtp_dict['smtp_user'], self.smtp_dict['mail_to'], str(msg))
            return 'Succeeded'
        except smtplib.SMTPException as e:
            return 'Error: {}'.format(e)
        finally:
            smtp_obj.close()


class Html:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('.'))
        self.template = self.env.get_template('kakuninsan/templates/base.html')

    def build_html(self, is_web, records, image_file_path):
        if is_web:
            dir_name, file_name = os.path.split(image_file_path)
            image = '{}/{}'.format(os.path.basename(dir_name), file_name)
        else:
            if image_file_path:
                with open(image_file_path, 'rb') as f:
                    data = base64.b64encode(f.read())
                image = 'data:image/png;base64,{}'.format(data.decode('utf-8'))
            else:
                image = ''
        contents = self.template.render(is_web=is_web, records=records, image=image)
        return contents
