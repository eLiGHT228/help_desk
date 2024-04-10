import streamlit as st
import time
from database.database import User, Ticket, engine
from sqlalchemy.orm import sessionmaker
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import sender_email, sender_password, send_to_admins, stconfig

class HelpDesk:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()  # Define session as needed

    def run(self):
        sign_out = st.button("Atsijungti", key='logout_btn')
        if sign_out:
            st.session_state["logged_in"] = False
            st.rerun()
        st.title("VRSA IT palaikymo sistema")
        with st.container(border=True):
            user_name = st.text_input('Vardas', value=st.session_state.get("user_fullname", ""), disabled=True)
            if st.session_state.get("room_nr", "") == None:
                room_nr = st.text_input('Kabinetas')
            else:
                room_nr = st.text_input('Kabinetas', value=st.session_state.get("room_nr", ""), disabled=True)
            ticket_name = st.text_input("Tema")
            category = st.selectbox("Kategorija", ("Įranga", "Programos", "Kita"), index=None, placeholder="Pasirinkite...")

            if category == "Įranga":
                category_type = st.selectbox("Įranga", ("Kompiuteris", "Skaitytuvas", "Spausdintuvas", "Kita"), index=None,
                                             placeholder="Pasirinkite...")

                if category_type == "Kompiuteris":
                    cat_type = st.selectbox("Problemos tipas", ("Kompiuterio paleidimas", "Kompiuterio prijungimas", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Skaitytuvas":
                    cat_type = st.selectbox("Problemos tipas", ("Skaitytuvo prijungimas", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Spausdintuvas":
                    cat_type = st.selectbox("Problemos tipas", ("Spausdintuvas prijungimas", "Tonerio keitimas", "Kita"),
                                            index=None, placeholder="Pasirinkite...")
                if category_type == "Kita":
                    cat_type = "Kita"

            if category == "Programos":
                category_type = st.selectbox("Programos", ("DVS", "Labbis", "Mokesta", "Parama", "Kita"), index=None,
                                             placeholder="Pasirinkite...")

                if category_type == "DVS":
                    cat_type = st.selectbox("Problemos tipas", ("Prijungimo klaidos", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Labbis":
                    cat_type = st.selectbox("Problemos tipas", ("Prijungimo klaidos", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Mokesta":
                    cat_type = st.selectbox("Problemos tipas", ("Prijungimo klaidos", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Parama":
                    cat_type = st.selectbox("Problemos tipas", ("Prijungimo klaidos", "Kita"), index=None,
                                            placeholder="Pasirinkite...")
                if category_type == "Kita" or category_type == "":
                    category_type, cat_type = "Kita", "Kita"

            if category == "Kita" or category == "":
                category, category_type, cat_type = "Kita", "Kita", "Kita"

            description = st.text_area("Komentaras")
            uploaded_file = st.file_uploader("Įterpti", type=['png', 'jpg'])

            if uploaded_file is not None:
                st.image(uploaded_file)

        submitted = st.button("Išsiųsti")

        if submitted:
            if not ticket_name or not room_nr or not category or not category_type or not cat_type or not description:
                st.error("Prašome užpildyti visus laukus!")
            else:
                existing_user = self.session.query(User).filter_by(name=user_name).first()

                if existing_user is None:
                    new_user = User(name=user_name, room_nr=room_nr)
                    self.session.add(new_user)
                    self.session.commit()
                else:
                    new_user = existing_user

                new_ticket = Ticket(user_id=new_user.id, topic=ticket_name, category=category,
                                    category_type=category_type, cat_type=cat_type, description=description,
                                    image_path=None, status="Sukurta", responsible=" ")

                if uploaded_file is not None:
                    with open("uploaded_images/" + uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    new_ticket.image_path = "uploaded_images/" + uploaded_file.name
                    uploaded_file.seek(0)

                self.session.add(new_ticket)
                self.session.commit()
                with st.spinner('Siųnčiama...'):
                    time.sleep(3)
                st.success(f"Ačiū, {user_name}! Tavo prašymas išsiųstas.")
                self.send_info(user_name, send_to_admins)

    def send_info(self, user_name, list):
        for receiver in list:
            # Create a multipart message and set headers
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = receiver
            message['Subject'] = 'Naujas tiketas'
            link = 'http://helpdesk:8501/'


            # Add body to email
            body = (f'Sveiki! \n \n {user_name} užregistravo naują tiketą! \n \n \n \n Palaikymo sistemos puslapio nuoroda: {link}')
            # f'<a href='){helpdesk:8501}'>Click here</a> '
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

if __name__ == "__main__":
    # Patikrina ar vartotojas yra prisijunges, jeigu ne tai perkelia prie prisijungimo lango, jeigu taip tai perkelia prie užduočių lango.
    if "logged_in" not in st.session_state:
        print("not")
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        print("help_desk")
        help_desk_app = HelpDesk()
        help_desk_app.run()
    else:
        stconfig()
        st.switch_page("pages/login.py")
