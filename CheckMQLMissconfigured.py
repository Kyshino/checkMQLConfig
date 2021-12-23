import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from os.path import join, dirname
from dotenv import load_dotenv
from dotenv import dotenv_values

def checkDotEnv():
    mandatoryVariables = ['EMAIL_FROM', 'EMAIL_PASSWORD','EMAIL_TO','EMAIL_SMTP','EMAIL_PORT','MQL_ID','MQL_COMMON_ROUTE']
    optionalVariables = ['EMAIL_SUBJECT']
    notIn = []
    optionalNotIn = []
    values = dotenv_values(join(dirname(__file__), '.env'))
    
    for variable in mandatoryVariables:
        if(variable not in values):
            notIn.append(variable)
    
    for variable in optionalVariables:
        if(variable not in values):
            optionalNotIn.append(variable)

    if(len(notIn) > 0):
        print("Tienes que configurar la/s variable/s {} en el .env".format(" ,".join(notIn)))

    if(len(optionalNotIn) > 0):
        print("No has configurado la/s variable/s {} en el .env, se usará la configuración por defecto.".format(", ".join(optionalNotIn)))
        
    return (len(notIn) == 0)

class CheckMetatrader:  
        
    def __init__(self, route, id):  
        self.route = route  
        self.id = id
        self.sellMode = "2"

    def getEmailMissconfiguredSubject(self):
        return  'Se ha desconfigurado la cuenta de MQL en el equipo <b>' + os.environ['COMPUTERNAME'] + '</b>.'
      
    def getEmailNotSellingSubject(self):
        return  'Se ha desconfigurado el check de MQL para vender el procesamiento en el equipo <b>' + os.environ['COMPUTERNAME'] + '</b>.'

    def getGenericHTML(self, message):
        return  """
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <title>Check Metatrader Missconfigured</title>
            </head>
            """+message+"""
            </html>
        """

    def check(self):  
        file = open(self.route, "r")
        lines = file.readlines()
        message = ''
        for line in lines:
            lineSplitted = line.split('=')
            if (line.startswith('Mode') and lineSplitted[1].rstrip() == self.sellMode):
                message = message + self.getEmailNotSellingSubject() + '<br>'
                print(self.getEmailNotSellingSubject())
            elif (line.startswith('Id') and lineSplitted[1].rstrip() == self.id):
                message = message + self.getEmailMissconfiguredSubject() + '<br>'
                print(self.getEmailMissconfiguredSubject())
        
        if(message != ''):
            subj = os.environ.get("EMAIL_SUBJECT") if ('EMAIL_SUBJECT' in dotenv_values(join(dirname(__file__), '.env'))) and os.environ.get("EMAIL_SUBJECT") != '' else 'Check Metatrader Missconfigured'
            email = Email(
                email = os.environ.get("EMAIL_FROM"),
                password = os.environ.get("EMAIL_PASSWORD"),
                message = self.getGenericHTML(message),
                subject = subj
                )
            email.sendMail()

class Email:
    def __init__(self, email, password, message, subject):
        self.emailFrom = email
        self.password = password
        self.subject = subject
        self.message = message
        self.smtp = os.environ.get('EMAIL_SMTP')
        self.port = os.environ.get('EMAIL_PORT')
        self.emailTo = os.environ.get('EMAIL_TO')

    def sendMail(self):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.emailFrom
        msg['To'] = self.emailTo
        msg.attach(MIMEText(self.message, 'html'))

        s = smtplib.SMTP(self.smtp + ':' + str(self.port))
        s.starttls()
        s.login(self.emailFrom, self.password)
        s.sendmail(self.emailFrom, self.emailTo, msg.as_string())
        s.quit()


if __name__ == "__main__":
    if (checkDotEnv()):
        load_dotenv(join(dirname(__file__), '.env'))
        checkMetaTrader = CheckMetatrader(
            route = os.environ.get("MQL_COMMON_ROUTE"),
            id = os.environ.get("MQL_ID")
            )
        
        checkMetaTrader.check()  
    else:
        exit