import smtplib
import pdb

from sendmail_config import Config
from email.mime.text import MIMEText

config = Config()


def sendalert(subj, statusmsg, mailboxes=config.get_notification_mailalert()):
    msg = MIMEText(statusmsg)
    msg['To'] = ",".join(mailboxes)
    msg['From'] = config.get_mailfrom()
    msg['Subject'] = subj

    server = smtplib.SMTP(
        host=config.get_mailserver(),
        port=config.get_mailserver_port()
    )
    server.starttls()
    server.login(config.get_mailuser(), config.get_mailpassword())

    try:
        server.sendmail(config.get_mailfrom(), mailboxes, msg.as_string())
    except Exception:
        pass
    finally:
        server.quit()
