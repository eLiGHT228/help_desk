# server config
server_address = 'ldap://10.230.242.2'
username = 'admindarole@vrsa.local'
password = 'MGSQLPython1991'
base_dn = 'dc=vrsa,dc=local'

database = 'sqlite:///database/helpdesk.db'

# mail

send_to_admins = ['darius.olechnovic@vrsa.lt']  # 'Vitalij.moroz@vrsa.lt', '', '', '', '', '']
email = 'darius.olechnovic@vrsa.lt'
mpassword = 'Vrsa2024*.'


def stconfig():
    import streamlit as st

    st.set_page_config(page_title="IT palaikymo sistema VRSA",
                       page_icon=":guardsman:",
                       layout="wide",
                       initial_sidebar_state=st.session_state.get('sidebar_state', 'collapsed'))

    st.markdown(
        """
    <style>
        body {
            background-color: #red; /* Change the color code to your desired background color */
        }
        [data-testid="collapsedControl"]{
            display: none;
            }
    </style>
    """,
        unsafe_allow_html=True,
    )
