import streamlit as st
import time
from database.database import User, Ticket, engine
from sqlalchemy.orm import sessionmaker
from integrations.AD import get_ad_users, get_AD_office
from mailing.mail import send_info

Session = sessionmaker(bind=engine)
session = Session()

def help_desk():

    listAD = get_ad_users()
    officeAD = get_AD_office()

    if st.button("Prisijungti"):
        st.switch_page("pages/dashboard.py")

    st.title("VRSA IT palaikymo sistema")

    with st.container(border=True):
        user_name = st.selectbox("Vardas ir Pavardė", listAD, label_visibility='visible')
        room_nr = st.selectbox("Kabineto nr.", officeAD)
        ticket_name = st.text_input("Tema")
        category = st.selectbox("Kategorija", ("Iranga", "Programos", "Kita"), index=None, placeholder="Pasirinkite...")

        if category == "Iranga":
            category_type = st.selectbox("Iranga", ("Kompiuteris", "Skaneris", "Printeris", "Kita"), index=None,
                                         placeholder="Pasirinkite...")

            if category_type == "Kompiuteris":
                cat_type = st.selectbox("Problemos tipas", ("Kompiuterio prijungimas", "Kita"), index=None,
                                        placeholder="Pasirinkite...")
            if category_type == "Skaneris":
                cat_type = st.selectbox("Problemos tipas", ("Skanerio prijungimas", "Kita"), index=None,
                                        placeholder="Pasirinkite...")
            if category_type == "Printeris":
                cat_type = st.selectbox("Problemos tipas", ("Printerio prijungimas", "Tonerio keitimas", "Kita"),
                                        index=None, placeholder="Pasirinkite...")
            if category_type == "Kita" or category_type == "":
                category_type, cat_type = "Kita", "Kita"

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
        uploaded_file = st.file_uploader("Iterpti", type=['png', 'jpg'])

        if uploaded_file is not None:
            st.image(uploaded_file)

    submitted = st.button("Išsiųsti")

    if submitted:

        if not user_name or not room_nr or not ticket_name or not category or not category_type or not cat_type or not description:
            st.error("Prašome užpildyti visus laukus!")

        else:
            existing_user = session.query(User).filter_by(name=user_name).first()

            if existing_user is None:
                new_user = User(name=user_name, room_nr=room_nr)
                session.add(new_user)
                session.commit()

            else:
                new_user = existing_user
            new_ticket = Ticket(user_id=new_user.id, topic=ticket_name, category=category, category_type=category_type, cat_type=cat_type,
                                description=description, image_path=None, status="Sukurta", responsible=" ")

            if uploaded_file is not None:
                # Save the uploaded file
                with open("uploaded_images/" + uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                new_ticket.image_path = "uploaded_images/" + uploaded_file.name
                uploaded_file.seek(0)

            session.add(new_ticket)
            session.commit()
            with st.spinner('Siųnčiama...'):
                time.sleep(3)
            st.success(f"Ačiū, {user_name}! Tavo prašymas išsiųstas.")
            send_info(user_name)
