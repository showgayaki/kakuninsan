import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate


class Mail:
    def __init__(self, smtp_dict):
        self.smtp_dict = smtp_dict.copy()

    def create_message(self, body_dict):
        msg = MIMEText(body_dict['body'])
        msg['Subject'] = body_dict['subject']
        msg['To'] = self.smtp_dict['mail_to']
        msg['Date'] = formatdate()
        return msg

    def send_mail(self, msg):
        try:
            smtp_obj = smtplib.SMTP(self.smtp_dict['smtp_server'], self.smtp_dict['smtp_port'])
            smtp_obj.ehlo()
            smtp_obj.starttls()
            smtp_obj.login(self.smtp_dict['smtp_user'], self.smtp_dict['smtp_pass'])
            smtp_obj.sendmail(self.smtp_dict['smtp_user'], self.smtp_dict['mail_to'], str(msg))
            return 'Succeeded'
        except smtplib.SMTPException:
            return 'Failed'
        finally:
            smtp_obj.close()
