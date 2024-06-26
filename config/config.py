# server config
server_address = 'ldap://10.230.242.2'
username = 'helpdeskVRSA@vrsa.local'
password = 'ITspec2024+'
base_dn = 'dc=vrsa,dc=local'

# mail

admin_email_list = ['darius.olechnovic@vrsa.lt']#, 'robert.kliukovski@vrsa.lt', 'Vitalij.moroz@vrsa.lt'] #, '', '', '', '', '']
sender_email = 'darius.olechnovic@vrsa.lt'
sender_password = 'Vrsa2024*.'

# database
DB_USERNAME = "root"
DB_PASSWORD = "ITspec2024+"
DB_NAME = "helpdeskdb"
SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USERNAME}:{DB_PASSWORD}@localhost:3306/helpdeskdb'



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
        .sidebar .sidebar-content {
            padding-left: 0 !important;
        }
        .sidebar .sidebar-content .collapse-button {
            display: none !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
