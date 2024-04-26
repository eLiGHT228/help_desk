import pandas as pd
from config.config import stconfig
import streamlit as st
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database.database import Base, Ticket, User, Comment  # Admin
from pages.login import StreamlitAuth
from config.config import stconfig, database
from integrations.AD import get_responsible
from streamlit_extras.stylable_container import stylable_container


class HelpdeskApp:
    def __init__(self):
        engine = create_engine(database)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.session = session()
        self.responsible = get_responsible()
        self.tickets = None
        self.tickets_per_page = 15
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = 1
        self.date_format = '%Y-%m-%d %H:%M'

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

    @staticmethod
    def show_headers():
        st.title('Užduočių sąrašas')
        colms = st.columns((1, 1, 1, 1, 1, 1, 1, 1))
        fields = ['ID', 'Ikelimo data', 'Vardas', 'Tema', 'Kategorija', 'Būsena', 'Atsakingas', '']

        for col, field_name in zip(colms, fields):
            col.write(field_name)  # header

    def ticket_list(self, function):
        function()

        total_tickets = self.tickets.count()
        total_pages = -(-total_tickets // self.tickets_per_page)  # Calculate total pages

        start_index = (st.session_state["current_page"] - 1) * self.tickets_per_page
        end_index = min(start_index + self.tickets_per_page, total_tickets)

        if self.tickets and function == self.load_data:
            if st.checkbox("Filtruoti", key=f"filter1"):
                self.filter_by_status()
            self.show_headers()
            for idx, (ticket, user) in enumerate(self.tickets[start_index:end_index]):
                self.display_ticket_info(idx, ticket, user, 'a')
            self.footbar(total_pages, 'A')


        elif self.tickets and function == self.load_my_data:
            if st.checkbox("Filtruoti", key=f"filter2"):
                self.filter_by_status()
            self.show_headers()
            for idx, (ticket, user) in enumerate(self.tickets[start_index:end_index]):
                self.display_ticket_info(idx, ticket, user, 'u')
            self.footbar(total_pages, "U")

        else:
            st.write('### No tickets found')

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

    #  visu užregistruotu užduočių ištraukimas iš duomenų bazes.
    def load_data(self):
        self.tickets = (self.session.query(Ticket, User).outerjoin(User, Ticket.user_id == User.id)
                        .order_by(desc(Ticket.created_date)))

        self.ticket_sts_counta = self.session.query(Ticket).filter_by(status='Sukurta').count()
        self.ticket_stv_counta = self.session.query(Ticket).filter_by(status='Vykdoma').count()
        self.ticket_sti_counta = self.session.query(Ticket).filter_by(status='Išspręsta').count()
        self.ticket_stu_counta = self.session.query(Ticket).filter_by(status='Uždaryta').count()

    #  prisijungusio vartotojo priskirtų užduočiu ištraukimas iš duomenų bazes.
    def load_my_data(self):
        self.tickets = (self.session.query(Ticket, User).outerjoin(User, Ticket.user_id == User.id)
                        .where(Ticket.responsible == st.session_state['user_fullname'])
                        .order_by(desc(Ticket.created_date)))
        self.ticket_stv_count = self.session.query(Ticket).filter_by(responsible=st.session_state['user_fullname'],
                                                                     status='Vykdoma').count()
        self.ticket_sti_count = self.session.query(Ticket).filter_by(responsible=st.session_state['user_fullname'],
                                                                     status='Išspręsta').count()
        self.ticket_stu_count = self.session.query(Ticket).filter_by(responsible=st.session_state['user_fullname'],
                                                                     status='Uždaryta').count()

    def display_ticket_info(self, idx, ticket, user, key):
        if ticket.responsible == " ":
            self.display_ticket_without_responsibility(idx, ticket, user, key)
        elif ticket.status == "Išspręsta" and ticket.responsible != " ":
            self.display_done_tickets(idx, ticket, user, key)
        else:
            self.display_ticket_with_responsibility(idx, ticket, user, key)

    def display_ticket_without_responsibility(self, idx, ticket, user, key):
        with stylable_container(key="container_with_border" + str(idx), css_styles="""
                                {
                                    border: 2px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                    background-color: rgba(238, 144, 144, 0.2); /* Transparent light red background */
                                }
                            """):
            self.display_ticket_columns(idx, ticket, user, key)

    def display_done_tickets(self, idx, ticket, user, key):
        with stylable_container(key="container_with_border2" + str(idx), css_styles="""
                                {
                                    border: 2px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                    background-color: rgba(144, 238, 144, 0.5); /* Transparent light green background */
                                }
                            """):
            self.display_ticket_columns(idx, ticket, user, key)

    def display_ticket_with_responsibility(self, idx, ticket, user, key):
        with stylable_container(key="container_with_border3" + str(idx), css_styles="""
                                {
                                    border: 2px solid rgba(49, 51, 63, 0.2);
                                    border-radius: 0.5rem;
                                    padding: calc(1em - 1px);
                                    background-color: rgba(144, 144, 144, 0.3); /* Transparent light green background */
                                }
                            """):
            self.display_ticket_columns(idx, ticket, user, key)

    def display_ticket_columns(self, idx, ticket, user, keyid):
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

            status_options = ("Sukurta", "Vykdoma", "Išspręsta", "Uždaryta")
            status_index = status_options.index(st.session_state["ticket_status" + keyid + str(idx)])
            status = st.selectbox("Būsena", options=status_options,
                                  help="Pasirinkite būseną...", index=status_index,
                                  placeholder=st.session_state["ticket_status" + keyid + str(idx)],
                                  key="selectbox" + keyid + str(idx) + "1")
            st.write(st.session_state["ticket_status" + keyid + str(idx)])
            responsible_index = self.responsible.index(
                st.session_state["ticket_responsible" + keyid + str(idx)])
            responsible = st.selectbox("Atsakingas", self.responsible, index=responsible_index,
                                       key="selectbox" + keyid + str(idx) + "2")

            save = st.button("Išsaugoti", key="button" + keyid + str(idx) + "-")

            if save:
                if status == "Sukurta" and responsible != " ":
                    status = "Vykdoma"
                self.update_ticket_status(ticket.id, status, responsible, idx, keyid)
                self.show_more = None
                del st.session_state["checkbox" + keyid + str(idx)]
                if "checkbox" + keyid + str(idx) not in st.session_state:
                    st.session_state["checkbox" + keyid + str(idx)] = False
                # send info to user
                st.rerun()

            with st.container(border=True):
                st.subheader("Komentarai")
                messages = self.session.query(Comment).filter_by(ticket_id=ticket.id)
                for comment in messages:
                    if comment.author_type == "Admin":
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
                                          , author_type="Admin", content=prompt)
                    self.session.add(new_message)
                    self.session.commit()
                    st.rerun()

    def update_ticket_status(self, ticket_id, new_status, responsible, idx, keyid):
        st.session_state["ticket_status" + keyid + str(idx)] = new_status
        st.session_state["ticket_responsible" + keyid + str(idx)] = responsible

        ticket = self.session.query(Ticket).filter_by(id=ticket_id).first()
        if ticket:
            ticket.status = new_status
            ticket.responsible = responsible
            self.session.commit()

    def result_view(self):
        self.load_my_data()
        st.write("### Jusu užduočių statistika")
        chart_data = pd.DataFrame(
            columns=["Vykdoma", "Išspręsta", "Uždaryta"],
            # [self.ticket_stv_count, self.ticket_sti_count, self.ticket_stu_count]
        )

        data = [dict(Busena='Vykdoma', Kiekis=self.ticket_stv_count),
                dict(Busena='Išspręsta', Kiekis=self.ticket_sti_count),
                dict(Busena='Uždaryta', Kiekis=self.ticket_stu_count)]

        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)

        st.write("### Visų užduočių statistika")
        data = [dict(Busena='Sukurta', Kiekis=self.ticket_sts_counta),
                dict(Busena='Vykdoma', Kiekis=self.ticket_stv_counta),
                dict(Busena='Išspręsta', Kiekis=self.ticket_sti_counta),
                dict(Busena='Uždaryta', Kiekis=self.ticket_stu_counta)]

        df = pd.DataFrame(data)
        st.dataframe(df, hide_index=True)

    def display_tickets(self):
        st.write(f'#### :male-astronaut: {st.session_state["user_fullname"]}')
        sign_out = st.button("Atsijungti", key='logout_btn')
        if sign_out:
            st.session_state["logged_in"] = False
            st.rerun()
        tab1, tab2, tab3 = st.tabs(["Užduotis", "Mano užduotis", "Statistika"])
        with tab1:
            self.ticket_list(self.load_data)
        with tab2:
            self.ticket_list(self.load_my_data)
        with tab3:
            self.result_view()


if __name__ == "__main__":

    stconfig()
    main = HelpdeskApp()
    app = StreamlitAuth()
    # Patikrina ar vartotojas yra prisijunges, jeigu ne tai perkelia prie prisijungimo lango, jeigu taip tai perkelia prie užduočių lango.
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        main.display_tickets()
    else:
        st.switch_page("pages/login.py")
