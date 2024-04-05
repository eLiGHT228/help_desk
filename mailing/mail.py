import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import email, mpassword, send_to_admins


def send_info(tuser, to_email=send_to_admins):

    for receiver in to_email:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message['From'] = email
        message['To'] = receiver
        message['Subject'] = 'Naujas tiketas'

        # Add body to email
        body = f'{tuser} užregistravo naują tiketą!'
        message.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()

        # Log in to Gmail account
        server.login(email, mpassword)

        # Send email
        server.send_message(message)

        # Quit the SMTP server
        server.quit()

