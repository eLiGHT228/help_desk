import streamlit as st
import time
from database.database import User, Ticket, engine, Comment
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import sender_email, sender_password, send_to_admins, stconfig
from datetime import datetime
from integrations.AD import get_responsible
from streamlit_extras.stylable_container import stylable_container


class HelpDesk:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()  # Define session as needed
        self.tickets = None
        self.responsible = get_responsible()
        self.tickets_per_page = 15
        self.placeholder = None
        self.userid = st.session_state.get("userid", "")
        self.user_fullname = st.session_state.get("user_fullname", "")
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1
        self.date_format = '%Y-%m-%d %H:%M'

    def run(self):
        sign_out = st.button("Atsijungti", key='logout_btn')
        if sign_out:
            st.session_state["logged_in"] = False
            st.rerun()
        tab1, tab2 = st.tabs(["Registruoti užduoti", "Mano užduotis"])
        with tab1:
            if st.session_state.get("user_fullname", "") == "Stanislav Sokolovskis":
                st.image('uploaded_images/20240412_124302.jpg', "Stanislavu")
            st.title("VRSA IT palaikymo sistema")
            with st.container(border=True):
                st.text_input('Vardas', value=self.user_fullname, disabled=True)
                if st.session_state.get("room_nr", "") == None:
                    room_nr = st.text_input('Kabinetas')
                else:
                    room_nr = st.text_input('Kabinetas', value=st.session_state.get("room_nr", ""), disabled=True)
                ticket_name = st.text_input("Tema")
                category = st.selectbox("Kategorija", ("Įranga", "Programos", "Kita"), index=None,
                                        placeholder="Pasirinkite...")

                if category == "Įranga":
                    category_type = st.selectbox("Įranga", ("Kompiuteris", "Skaitytuvas", "Spausdintuvas", "Kita"),
                                                 index=None,
                                                 placeholder="Pasirinkite...")

                    if category_type == "Kompiuteris":
                        cat_type = st.selectbox("Problemos tipas", ("Kompiuterio paleidimas", "Kompiuterio prijungimas",
                                                                    "Kita"), index=None,
                                                placeholder="Pasirinkite...")
                    if category_type == "Skaitytuvas":
                        cat_type = st.selectbox("Problemos tipas", ("Skaitytuvo prijungimas", "Kita"), index=None,
                                                placeholder="Pasirinkite...")
                    if category_type == "Spausdintuvas":
                        cat_type = st.selectbox("Problemos tipas", ("Spausdintuvas prijungimas", "Tonerio keitimas",
                                                                    "Kita"),
                                                index=None, placeholder="Pasirinkite...")
                    if category_type == "Kita":
                        cat_type = "Kita"

                if category == "Programos":
                    category_type = st.selectbox("Programos", ("DVS", "Labbis", "Mokesta", "Parama", "Kita"),
                                                 index=None,
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
                    existing_user = self.session.query(User).filter_by(id=self.userid).first()

                    if existing_user is None:
                        new_user = User(id=self.userid, name=self.user_fullname, room_nr=room_nr)
                        self.session.add(new_user)
                        self.session.commit()
                    # else:
                        # new_user = existing_user
                    self.id_maker(category, category_type)

                    new_ticket = Ticket(id=self.unique_id + datetime.now().strftime("%m%d%H%M%S"), user_id=self.userid,
                                        topic=ticket_name, category=category,
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
                    st.success(f"Ačiū, {self.user_fullname}! Tavo prašymas išsiųstas.")
                    self.send_info(self.user_fullname, send_to_admins)
        with tab2:
            self.tickets = (self.session.query(Ticket, User).outerjoin(Ticket.user)
                            .filter(User.name == st.session_state.get("user_fullname", ""))
                            .order_by(desc(Ticket.created_date)))

            total_tickets = self.tickets.count()
            total_pages = -(-total_tickets // self.tickets_per_page)  # Calculate total pages

            start_index = (st.session_state["current_page"] - 1) * self.tickets_per_page
            end_index = min(start_index + self.tickets_per_page, total_tickets)

            if self.tickets:
                if st.checkbox("Filtruoti", key=f"filter"):
                    self.tickets = self.filter_by_status()
                self.show_headers()
                for idx, (ticket, user) in enumerate(self.tickets[start_index:end_index]):
                    self.display_ticket_info(idx, ticket, user, 'a')
                self.footbar(total_pages, 'A')

    def display_ticket_info(self, idx, ticket, user, keyid):
        with st.container(border=True):
            col1, col2, col4, col5, col6, col7, col8, col9 = st.columns((1, 1, 1, 1, 1, 1, 1, 1))
            col1.write(ticket.id)  # index
            col2.write(str(ticket.created_date)[0:16])
            col4.write(user.name)
            col5.write(ticket.topic)
            col6.write(ticket.category_type)
            col7.write(ticket.status)
            if "ticket_status" + keyid + str(idx) not in st.session_state:
                st.session_state["ticket_status" + keyid + str(idx)] = ticket.status
            col8.write(ticket.responsible)
            if "ticket_responsible" + keyid + str(idx) not in st.session_state:
                st.session_state["ticket_responsible" + keyid + str(idx)] = ticket.responsible

            self.placeholder = col9.empty()  # create a placeholder
            self.show_more_btn = self.placeholder.checkbox("Detaliau", key="checkbox" + keyid + str(idx))
            if self.show_more_btn:
                self.show_more(ticket, user, keyid, idx)

    def show_more(self, ticket, user, keyid, idx):
        with st.container(border=True):

            st.write("Užduoties informacija:")
            with st.container(border=True):
                st.write("Kabinetas: " + str(user.room_nr))
            with st.container(border=True):
                st.write("Komentaras: " + ticket.description)

            if ticket.image_path:
                st.image(ticket.image_path, width=500)
            else:
                st.write("Nėra jokiu paveiksliukų")
            st.write(st.session_state["ticket_status" + keyid + str(idx)])
            with st.container(border=True):
                st.subheader("Komentarai")
                messages = self.session.query(Comment).filter_by(ticket_id=ticket.id)
                for comment in messages:
                    if comment.author_type == "User":
                        with stylable_container(key="Container" + str(comment.id) + keyid + str(idx), css_styles="""
                                {
                                    border: 2px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                    background-color: rgba(144, 238, 144, 0.5); /* Transparent light green background */
                                }
                            """):
                            with st.chat_message("user"):
                                st.write(comment.post_date)
                                st.write(comment.author)
                                st.write(comment.content)
                    else:
                        with stylable_container(key="Container" + str(comment.id) + keyid + str(idx), css_styles="""
                                {
                                    border: 2px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                    background-color: rgba(144, 144, 144, 0.5); /* Transparent light green background */
                                }
                            """):
                            with st.chat_message("user"):
                                st.write(comment.post_date)
                                st.write(comment.author)
                                st.write(comment.content)
                prompt = st.chat_input("Komentaras", key="ch_i" + keyid + str(idx))
                if prompt:
                    new_message = Comment(ticket_id=ticket.id, author=st.session_state.get("user_fullname", "")
                                          , author_type="User", content=prompt)
                    self.session.add(new_message)
                    self.session.commit()
                    st.rerun()

    def filter_by_status(self):
        filters = st.selectbox("Filtruoti pagal:", ("Kategorija", "Būsena", "Atsakingas"), index=None,
                               placeholder="Pasirinkite pagal ką filtruosite")
        if filters == "Kategorija":
            selected_filter = st.selectbox(
                "Filtruoti pagal kategoriją",
                ("Iranga", "Programos", "Kita"),
            )
            self.tickets = self.tickets.filter(Ticket.category == selected_filter)
        if filters == "Būsena":
            selected_filter = st.selectbox(
                "Filtruoti pagal būseną",
                ("Sukurta", "Vykdoma", "Išspręsta", "Uždaryta"),
            )
            self.tickets = self.tickets.filter(Ticket.status == selected_filter)
        if filters == "Atsakingas":
            selected_filter = st.selectbox(
                "Filtruoti pagal atsakingą",
                self.responsible,
            )
            self.tickets = self.tickets.filter(Ticket.responsible == selected_filter)
        return self.tickets
    def show_headers(self):
        st.title('Užduočių sąrašas')
        colms = st.columns((1, 1, 1, 1, 1, 1, 1, 1))
        fields = ['ID', 'Ikelimo data', 'Vardas', 'Tema', 'Kategorija', 'Būsena', 'Atsakingas', '']

        for col, field_name in zip(colms, fields):
            col.write(field_name)  # header

    def footbar(self, total_pages, id):
        st.write(f"Page: {st.session_state["current_page"]}")
        prev_btn, _, next_btn = st.columns(3)
        if st.session_state["current_page"] > 1:
            if prev_btn.button("Prev", key=f'prevbtn{id}'):
                st.session_state["current_page"] -= 1
                st.rerun()
        if st.session_state["current_page"] < total_pages:
            if next_btn.button("Next", key=f'nextbtn{id}'):
                st.session_state["current_page"] += 1
                st.rerun()
    def id_maker(self, cat, cat_type):
        if cat == "Įranga" and cat_type == "Kompiuteris":
            self.unique_id = "IKO"
        elif cat == "Įranga" and cat_type == "Skaitytuvas":
            self.unique_id = "ISK"
        elif cat == "Įranga" and cat_type == "Spausdintuvas":
            self.unique_id = "ISP"
        elif cat == "Įranga" and cat_type == "Kita":
            self.unique_id = "IKI"
        elif cat == "Programos" and cat_type == "DVS":
            self.unique_id = "PD"
        elif cat == "Programos" and cat_type == "Labbis":
            self.unique_id = "PL"
        elif cat == "Programos" and cat_type == "Mokesta":
            self.unique_id = "PM"
        elif cat == "Programos" and cat_type == "Parama":
            self.unique_id = "PP"
        elif cat == "Programos" and cat_type == "Kita":
            self.unique_id = "PKI"
        else:
            self.unique_id = "KI"


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
    stconfig()
    # Patikrina ar vartotojas yra prisijunges, jeigu ne tai perkelia prie prisijungimo lango, jeigu taip tai perkelia prie užduočių lango.
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        help_desk_app = HelpDesk()
        help_desk_app.run()
    else:
        st.switch_page("pages/login.py")
