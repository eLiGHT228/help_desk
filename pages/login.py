import streamlit as st
import streamlit_authenticator as stauth
import time
from integrations.AD import connect_AD, get_fullname, get_fullname_u, get_office

class StreamlitAuth:
    def __init__(self):
        self.logged_in = False
        if "user_name" not in st.session_state:
            st.session_state["user_name"] = "Guest"
        if "user_fullname" not in st.session_state:
            st.session_state["user_fullname"] = "Guest"
        if "room_nr" not in st.session_state:
            st.session_state['room_nr'] = None
        # self.run()

    def run(self):

        st.title("Prisijungti")
        st.subheader("")

        self.user_name = st.text_input("Vartotojo vardas")
        self.password = st.text_input("Slaptažodis", type='password')

        if st.button("Prisijungti"):
            if connect_AD(usrnm=self.user_name+'@vrsa.local', psswrd=self.password):
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = self.user_name
                self.check_roles()
            else:
                st.error("Blogai ivesti duomenys!")
    def check_roles(self):
        if st.session_state["user_name"][0:5] == 'admin':
            if st.session_state["user_name"] == 'adminrobkli':
                st.session_state["user_fullname"] = get_fullname('adminrobkliu')
            else:
                st.session_state["user_fullname"] = get_fullname(st.session_state["user_name"])

            with st.spinner(''):
                time.sleep(1)
                st.success('Prisijungimas sėkmingas!')
                st.switch_page("pages/dashboard.py")
        else:
            st.session_state["user_fullname"] = get_fullname_u(st.session_state["user_name"])
            st.session_state['room_nr'] = get_office(st.session_state["user_name"])
            with st.spinner(''):
                time.sleep(1)
                st.success('Prisijungimas sėkmingas!')
                st.switch_page("pages/ticket_register.py")



if __name__ == "__main__":
    # Patikrina ar vartotojas yra prisijunges, jeigu ne tai perkelia prie prisijungimo lango, jeigu taip tai perkelia prie užduočių lango.
    app = StreamlitAuth()
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if st.session_state["logged_in"]:
        app.check_roles()
    else:
        app.run()
