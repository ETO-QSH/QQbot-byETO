import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
    def __init__(self, username, password):
        self.smtp = smtplib.SMTP_SSL('smtp.qq.com', 465)
        self.smtp.login(username, password)
        self.email_body = MIMEMultipart()
        self.email_from_username = username

    def generate_email_body(self, email_to_list, email_title, email_content):
        self.email_body['Subject'] = email_title
        self.email_body['From'] = self.email_from_username
        self.email_body['To'] = ",".join(email_to_list)

        # 添加邮件正文
        text_plain = MIMEText(email_content, 'plain', 'utf-8')
        self.email_body.attach(text_plain)

    def send_email(self, email_to_list):
        self.smtp.sendmail(self.email_from_username, email_to_list, self.email_body.as_string())

    def exit(self):
        self.smtp.quit()

def email_sender(item, username='3078491964@qq.com', password='lgphyahullqvdgjc'):
    email_sender = EmailSender(username, password)
    email_to_list = ['3078491964@qq.com']
    email_title = 'Python123ETO'
    email_content = str(item)
    email_sender.generate_email_body(email_to_list, email_title, email_content)
    email_sender.send_email(email_to_list)
    email_sender.exit()
