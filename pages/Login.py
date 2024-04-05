import streamlit as st
import time
from integrations.AD import connect_AD, get_fullname

class StreamlitAuth:
    def __init__(self):
        self.logged_in = False
        if "user_name" not in st.session_state:
            st.session_state["user_name"] = "Guest"
        if "user_fullname" not in st.session_state:
            st.session_state["user_fullname"] = "Guest"
        self.login()

    def login(self):


        if st.button("Registruoti tiketą"):
            st.switch_page("app.py")

        st.title("Login VRSA")
        st.subheader("")

        self.user_name = st.text_input("Username")
        self.password = st.text_input("Slaptažodis", type='password')

        if st.button("Prisijungti"):
            if connect_AD(usrnm=self.user_name+'@vrsa.local', psswrd=self.password):
                st.session_state["logged_in"] = True
                st.session_state["user_name"] = self.user_name
                if self.user_name == 'adminrobkli':
                    st.session_state["user_fullname"] = get_fullname('adminrobkliu')
                else:
                    st.session_state["user_fullname"] = get_fullname(self.user_name)
                with st.spinner(''):
                    time.sleep(2)
                    st.success('Login successful!')
                    st.switch_page("pages/dashboard.py")

            else:
                time.sleep(1)
                st.error('Invalid username or password')


    def main_page(self):
        st.switch_page("pages/dashboard.py")