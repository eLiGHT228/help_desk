import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import sender_email, sender_password, admin_email_list
from sqlalchemy.orm import sessionmaker
from database.database import User, engine

def get_mail(userid):

    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(id=userid).first()

    return user.email

def mail_for_user(mail_type, receivers, ticket_id, ticket_title, timestamp,
                  description=None, new_status=None, comment=None):
    global subject, body
    link = 'https://helpdesk.vrsa.lt/'

    if mail_type == 1:

        subject = f"Užduotis užregistruota - {ticket_id}"
        body = (
            f"""Sveiki,

            Jūsų užduotis buvo sėkmingai užregistruota mūsų sistemoje.
            
            **Užduoties ID:** {ticket_id}
            **Pavadinimas:** {ticket_title}
            **Aprašymas:** {description}
            **Registravimo data:** {timestamp}
            
            Mūsų komanda netrukus pradės darbą su jūsų užduotimi.
            
            Dėkojame, kad naudojatės mūsų paslaugomis!
            
            Pagarbiai,
            IT skyrius
            Vilniaus rajono savivaldybės administracija
            
            Prisijunkite prie mūsų sistemos čia: {link}
            """)

    elif mail_type == 2:

        subject = f"Užduoties būsenos atnaujinimas - {ticket_id}"
        body = (
            f"""Sveiki,

            Norime jus informuoti, kad jūsų užduoties būseną buvo atnaujinta.

            **Užduoties ID:** {ticket_id}
            **Pavadinimas:** {ticket_title}
            **Nauja būsena:** {new_status}
            **Atnaujinimo data:** {timestamp}

            Pagarbiai,
            IT skyrius
            Vilniaus rajono savivaldybės administracija

            Prisijunkite prie mūsų sistemos čia: {link}
            """)

    elif mail_type == 3:

        subject = f"Naujas komentaras užduotyje - {ticket_id}"
        body = (
            f"""Sveiki,

            Jūsų užduotyje buvo paliktas naujas komentaras.

            **Užduoties ID:** {ticket_id}
            **Pavadinimas:** {ticket_title}
            **Komentaras:** {comment}
            **Komentaro data:** {timestamp}
            
            Jei turite papildomų klausimų ar norite atsakyti į šį komentarą, prašome prisijungti prie mūsų sistemos.

            Dėkojame, kad naudojatės mūsų paslaugomis!

            Pagarbiai,
            IT skyrius
            Vilniaus rajono savivaldybės administracija

            Prisijunkite prie mūsų sistemos čia: {link}
            """)

    send_mail(receivers, subject, body)

def mail_for_IT(mail_type, ticket_id, ticket_title, timestamp, receivers=admin_email_list, description=None,
                comment=None):
    global subject, body
    link = 'https://helpdesk.vrsa.lt/'

    if mail_type == 1:

        subject = f"Užduotis užregistruota - {ticket_id}"
        body = (
            f"""Sveiki,

            Nauja užduotis buvo užregistruota IT palaikymo sistemoje.

            **Užduoties ID:** {ticket_id}
            **Pavadinimas:** {ticket_title}
            **Aprašymas:** {description}
            **Registravimo data:** {timestamp}

            Pagarbiai,
            IT skyrius
            Vilniaus rajono savivaldybės administracija

            Prisijunkite prie mūsų sistemos čia: {link}
            """)

    elif mail_type == 2:

        subject = f"Naujas komentaras užduotyje - {ticket_id}"
        body = (
            f"""Sveiki,

            {ticket_id} užduotyje buvo paliktas naujas komentaras.

            **Užduoties ID:** {ticket_id}
            **Pavadinimas:** {ticket_title}
            **Komentaras:** {comment}
            **Komentaro data:** {timestamp}

            Pagarbiai,
            IT skyrius
            Vilniaus rajono savivaldybės administracija

            Prisijunkite prie mūsų sistemos čia: {link}
            """)

    send_mail(receivers, subject, body)

def send_mail(receivers, subject, body):
    for receiver in receivers:
        # Create a multipart message and set headers
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()

        try:
            # Log in to email account
            server.login(sender_email, sender_password)

            # Send email
            server.send_message(message)
            print(f"Email sent to {receiver}")
        except Exception as e:
            print(f"Failed to send email to {receiver}: {e}")
        finally:
            # Quit the SMTP server
            server.quit()

