import asyncio
import os

import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from inzerator.users.emails import EmailStorage

from datetime import datetime

MAIL_PARAMS = {'TLS': True, 'host': os.environ.get("SMTP_URL"), 'password': os.environ.get("SMTP_PASSWORD"),
               'user': os.environ.get("SMTP_USER"), 'port': os.environ.get("SMTP_PORT")}


class EmailSender:

    def __init__(self, email_storage: EmailStorage):
        self.email_storage = email_storage

    async def send_emails(self):
        for e in await self.email_storage.get_to_send(datetime.now()):
            await self.send_mail(e.user.email, e.text)
            await self.email_storage.remove(e.id)

    async def send_mail(self, to: str, text: str):
        print(f"sending to %s : %s" % (to, text))
        await send_mail_async(os.environ.get("SEND_FROM"), [to], "Inzerator", text)
        print(f"sent to: " + to)


async def send_mail_async(sender, to, subject, text, textType='plain', **params):
    """Send an outgoing email with the given parameters.

    :param sender: From whom the email is being sent
    :type sender: str

    :param to: A list of recipient email addresses.
    :type to: list

    :param subject: The subject of the email.
    :type subject: str

    :param text: The text of the email.
    :type text: str

    :param textType: Mime subtype of text, defaults to 'plain' (can be 'html').
    :type text: str

    :param params: An optional set of parameters. (See below)
    :type params; dict

    Optional Parameters:
    :cc: A list of Cc email addresses.
    :bcc: A list of Bcc email addresses.
    """

    # Default Parameters
    cc = params.get("cc", [])
    bcc = params.get("bcc", [])
    mail_params = params.get("mail_params", MAIL_PARAMS)

    # Prepare Message
    msg = MIMEMultipart()
    msg.preamble = subject
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    if len(cc): msg['Cc'] = ', '.join(cc)
    if len(bcc): msg['Bcc'] = ', '.join(bcc)

    msg.attach(MIMEText(text, textType, 'utf-8'))

    # Contact SMTP server and send Message
    host = mail_params.get('host', 'localhost')
    isSSL = mail_params.get('SSL', False)
    isTLS = mail_params.get('TLS', False)
    port = mail_params.get('port', 465 if isSSL else 25)
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=isSSL)
    await smtp.connect()
    if isTLS:
        await smtp.starttls()
    if 'user' in mail_params:
        await smtp.login(mail_params['user'], mail_params['password'])
    await smtp.send_message(msg)
    await smtp.quit()


if __name__ == "__main__":
    email = "mcivanqutest@gmail.com"
    co1 = send_mail_async(email,
                          ["martin.civan5@gmail.com"],
                          "Test 1",
                          'Test 1 '
                          'https://www.bazos.sk'
                          'Message',
                          textType="plain")
    # co2 = send_mail_async(email,
    #                       [email],
    #                       "Test 2",
    #                       'Test 2 Message',
    #                       textType="plain")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(co1))
    loop.close()
