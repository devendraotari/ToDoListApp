import smtplib
from email.message import EmailMessage

class EmailSender:
    def __init__(self,content,to_email):
        self.content=content
        self.to_email=to_email
        self.email = EmailMessage()
        self.email['from'] = 'Devendra Otari'
        self.email['to'] = self.to_email
        self.email['subject'] = 'temporary password to login'
        self.email.set_content(f'you temporary password is {self.content}')

        self.smtp = smtplib.SMTP(host='smtp.gmail.com',port=587 )
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login('mockinterviewcdac@gmail.com','MockInterview12#4')
    
    def sendEmail(self):
        self.smtp.send_message(self.email)
        print("message is sent")



