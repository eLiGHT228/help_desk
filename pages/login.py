import streamlit as st
from config.config import stconfig, server_address, base_dn
import time
from integrations.AD import connect_AD, get_fullname, get_fullname_u, get_office

class StreamlitAuth:
    def __init__(self):
        self.logged_in = False
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = None
        if "user_fullname" not in st.session_state:
            st.session_state["user_fullname"] = None
        if "room_nr" not in st.session_state:
            st.session_state['room_nr'] = None

    def run(self):
        col1, col2, col3 = st.columns((1, 20, 1))
        col1.image("helpdesk-logo.png", width=65)
        col2.header("VRSA IT Palaikymo Sistema", divider="red")
        col2.write("padės mums geriau ir efektyviau valdyti bei spręsti visus Jūsų pagalbos prašymus ir IT užduotis")
        st.title("Prisijungti")
        st.subheader("")

        self.user_name = st.text_input("Vartotojo vardas")
        self.password = st.text_input("Slaptažodis", type='password')

        if st.button("Prisijungti"):
            if connect_AD(usrnm=self.user_name+'@vrsa.local', psswrd=self.password):
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = self.user_name
                self.check_roles()
            else:
                st.error("Blogai ivesti duomenys!")
    def check_roles(self):
        if st.session_state["user_id"][0:5] == 'admin':
            if st.session_state["user_id"] == 'adminrobkli':
                st.session_state["user_fullname"] = get_fullname('adminrobkliu')
            else:
                st.session_state["user_fullname"] = get_fullname(st.session_state["user_id"])
            with st.spinner(''):
                time.sleep(1)
                st.success('Prisijungimas sėkmingas!')
                time.sleep(1)
                st.switch_page("pages/dashboard.py")
        else:
            st.session_state["user_fullname"] = get_fullname_u(st.session_state["user_id"])
            st.session_state['room_nr'] = get_office(st.session_state["user_id"])
            with st.spinner(''):
                time.sleep(1)
                st.success('Prisijungimas sėkmingas!')
                st.switch_page("pages/ticket_register.py")



if __name__ == "__main__":
    stconfig()
    # Patikrina ar vartotojas yra prisijunges, jeigu ne tai perkelia prie prisijungimo lango, jeigu taip tai perkelia prie užduočių lango.
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        app = StreamlitAuth()
        app.check_roles()
    else:
        app = StreamlitAuth()
        app.run()
