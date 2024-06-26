import streamlit as st
import time
from database.database import User, Ticket, engine, Comment, TicketStatus
from sqlalchemy import desc, or_
from sqlalchemy.orm import sessionmaker
from config.config import stconfig
from mailing.mail import mail_for_user, mail_for_IT, get_mail
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
        self.userid = st.session_state.get("user_id", "")
        self.email = [get_mail(self.userid)]
        self.user_fullname = st.session_state.get("user_fullname", "")
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1
        self.date_format = '%Y-%m-%d %H:%M'

    def run(self):
        col1, col2, col3 = st.columns((1, 20, 2))
        col1.image("helpdesk-logo.png", width=65)
        col2.header("VRSA IT Palaikymo Sistema", divider="red")
        col3.write(f'###### :male-astronaut: {st.session_state["user_fullname"]}')
        sign_out = col3.button("Atsijungti", key='logout_btn')
        if sign_out:
            st.session_state["logged_in"] = False
            st.rerun()
        tab1, tab2 = st.tabs(["Registruoti užduoti", "Mano užduotis"])
        with tab1:
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

                priority = st.selectbox("Svarbumo lygis", ("Mažas", "Vidutinis", "Didelis"), index=None,
                                        placeholder="Pasirinkite...")
                description = st.text_area("Komentaras")
                uploaded_file = st.file_uploader("Įterpti", type=['png', 'jpg'])

                if uploaded_file is not None:
                    st.image(uploaded_file)

            submitted = st.button("Išsiųsti")

            if submitted:
                if not ticket_name or not room_nr or not category or not category_type or not cat_type or not description:
                    st.error("Prašome užpildyti visus laukus!")
                else:
                    try:
                        self.id_maker(category, category_type)
                        ticket_id = self.unique_id + datetime.now().strftime("%m%d%H%M%S")
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

                        ticket_status = TicketStatus(ticket_id=ticket_id, author=st.session_state["user_fullname"],
                                                     status="Sukurta")

                        self.session.add(ticket_status)

                        ticket_comment = Comment(ticket_id=ticket_id, author=st.session_state.get("user_fullname", "")
                                                  , author_type="User", content=description)
                        self.session.add(ticket_comment)
                        self.session.commit()
                        with st.spinner('Siųnčiama...'):
                            time.sleep(3)
                        st.success(f"Ačiū, {self.user_fullname}! Tavo prašymas su ID: {ticket_id} išsiųstas.")
                        mail_for_user(1, receivers=self.email, ticket_id=ticket_id, ticket_title=ticket_name,
                                      timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description=description)
                        mail_for_IT(1, ticket_id=ticket_id, ticket_title=ticket_name,
                                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), description=description)
                    except Exception as e:
                        st.error("Jūsų užklausą nepavyko išsaugoti. Prašome pabandyti dar kartą po kurio laiko.")

        with tab2:
            self.tickets = (self.session.query(Ticket, User).outerjoin(User, Ticket.user_id == User.id)
                            .filter(User.name == st.session_state.get("user_fullname", ""))
                            .order_by(desc(Ticket.created_date)))

            total_tickets = self.tickets.count()
            total_pages = -(-total_tickets // self.tickets_per_page)  # Calculate total pages

            start_index = (st.session_state["current_page"] - 1) * self.tickets_per_page
            end_index = min(start_index + self.tickets_per_page, total_tickets)

            colms1, colms2 = st.columns((1, 4))
            pattern_word = colms1.text_input("Paieška:", key="search1")
            search_btn = colms1.button("Ieškoti")
            ticket_filter = colms2.checkbox("Filtruoti", key=f"filter")
            if search_btn:
                self.tickets = self.search(pattern_word)
            if ticket_filter:
                self.tickets = self.filter_by()
            if self.tickets.count()>0:
                self.show_headers()
                for idx, (ticket, user) in enumerate(self.tickets[start_index:end_index]):
                    self.display_ticket_info(idx, ticket, user, 'a')
                self.footbar(total_pages, 'A')
            else:
                st.title("Užduočių nėra.")

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

    @st.experimental_dialog("Ištrinti užduotį")
    def submit_ticket_delete(self,ticket):
        st.write("Pašalinus užduoti ją nebegalima bus atkurt.")
        st.write("Ar tikrai norite ištrinti užduotį?")
        colum1, colum2 = st.columns((1, 1))
        if colum1.button("Taip"):
            self.delete_ticket(ticket.id)
            st.success("Užduotis pašalinta!")
            self.uncheck_all_checkboxes()
            time.sleep(1)
            st.rerun()
        if colum2.button("Ne"):
            st.rerun()

    def show_more(self, ticket, user, keyid, idx):
        colm1, colm2 = st.columns([6, 2])
        with colm1.container(border=True):
            st.write("Užduoties informacija:")
            with st.container(border=True):
                st.write("Ikelimo data: " + str(ticket.created_date)[0:16])
            with st.container(border=True):
                st.write("Užsakovas: " + user.name)
            with st.container(border=True):
                st.write("Kabinetas: " + str(user.room_nr))

            if ticket.image_path:
                st.image(ticket.image_path, width=500)
            else:
                st.write("Nėra jokiu paveiksliukų")
            tb1, tb2 = st.tabs(["Komentarai", "Užduoties istorija"])
            with tb1:
                with st.container(border=True):
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
                                    st.write(str(comment.post_date)[0:16])
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
                                    st.write(str(comment.post_date)[0:16])
                                    st.write(comment.author)
                                    st.write(comment.content)
                    prompt = st.chat_input("Komentaras", key="ch_i" + keyid + str(idx))
                    if prompt:
                        try:
                            new_message = Comment(ticket_id=ticket.id, author=st.session_state.get("user_fullname", "")
                                                  , author_type="User", content=prompt)
                            self.session.add(new_message)
                            mail_for_IT(2, ticket_id=ticket.id, ticket_title=ticket.topic,
                                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), comment=prompt)

                            self.session.commit()
                            st.rerun()
                        except Exception as e:
                            st.error("Jūsų kommentaro nepavyko pridėti. Prašome pabandyti dar kartą po kurio laiko.")

            with tb2:
                status_history = self.session.query(TicketStatus).filter_by(ticket_id=ticket.id)
                if status_history:
                    for statuses in status_history:
                        with st.container(border=True):
                            cols1, cols2 = st.columns(2)
                            with cols1:
                                st.write(f"Jūsų užklausos būsena pakeista į : {statuses.status}")
                            with cols2:
                                st.write(f"|{str(statuses.status_date)[0:16]}|")
                else:
                    st.write("nera istorijos")
        with colm2.container(border=True):
            with st.container(border=True):
                st.write(f"Būsena: {ticket.status}")
            with st.container(border=True):
                st.write(f"Užklausos tipas: {ticket.category}")


            rem_ticket = st.button("Ištrinti užduoti", key=keyid + str(idx))
            if rem_ticket:
                try:
                    self.submit_ticket_delete(ticket)
                except Exception as e:
                    st.error("Nepavyko pašalinti užduoties. Prašome pabandyti dar kartą po kurio laiko.")

    def delete_ticket(self, ticket_id):
        ticket_to_delete = self.session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if ticket_to_delete:
            self.session.delete(ticket_to_delete)
            self.session.commit()

        else:
            st.error("Įrašo rasti nepavyko.")

    def uncheck_all_checkboxes(self):
        # Iterate over all items in session state and uncheck checkboxes
        for key in st.session_state.keys():
            if key.startswith("checkbox"):
                del st.session_state[key]
                if key not in st.session_state:
                    st.session_state[key] = False

    def search(self, search_word):
        search_pattern = f"%{search_word}%"
        self.tickets = self.tickets.filter(
            or_(
                Ticket.id.like(search_pattern),
                Ticket.created_date.like(search_pattern),
                User.name.like(search_pattern),
                Ticket.topic.like(search_pattern),
                Ticket.category_type.like(search_pattern),
                Ticket.status.like(search_pattern),
                Ticket.responsible.like(search_pattern)
            )
        )
        return self.tickets

    def filter_by(self):
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
        fields = ['ID', 'Įkėlimo data', 'Vardas', 'Tema', 'Kategorija', 'Būsena', 'Atsakingas', '']

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
