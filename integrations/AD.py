from ldap3 import Server, Connection, ALL
from config.config import server_address, username, password, base_dn

blacklist = ['admindarlip', 'adminerngin']
def connect_AD(usrnm=username, psswrd=password):
    server = Server(server_address, get_info=ALL)
    try:
        conn = Connection(server, user=usrnm, password=psswrd, auto_bind=True)
        return conn
    except:
        return False
    # return conn


def get_ad_users():
    listAD = dict()
    listAD[""] = ""

    try:
        # Establish connection
        conn = connect_AD()

        # Search for users
        conn.search(base_dn, '(&(objectClass=user)(|(givenName=*)(sn=*)))', attributes=['givenName', 'sn', 'mail'])

        # Iterate over search results
        for entry in conn.entries:
            try:
                listAD[entry['givenName'].value + " " + entry['sn'].value] = entry['mail'].value
            except:
                pass  # Ignore any errors and continue processing

        # Close the connection when done
        conn.unbind()
        return listAD

    except Exception as e:
        print(f"An error occurred: {e}")


def get_AD_office():
    office_numbers = set()
    office_numbers.add("")

    try:
        # Establish connection
        conn = connect_AD()

        # Search for users with office numbers
        conn.search(base_dn, '(&(objectClass=user)(physicalDeliveryOfficeName=*))',
                    attributes=['physicalDeliveryOfficeName'])

        # Iterate over search results
        for entry in conn.entries:
            try:
                office_number = entry['physicalDeliveryOfficeName'][0]
                # Check if the office number has exactly 3 digits
                if len(office_number) == 3 and office_number.isdigit():
                    office_numbers.add(office_number)
            except Exception as e:
                print(f"Error processing entry: {e}")

        # Close the connection when done
        conn.unbind()

        sorted_office_numbers = sorted(office_numbers)

        return sorted_office_numbers

    except Exception as e:
        print(f"An error occurred: {e}")

def get_fullname(admin):

    from ldap3 import Server, Connection, SUBTREE
    from config.config import server_address, username, password, base_dn

    # Connect to the AD server
    server = Server(server_address)
    conn = Connection(server, user=username, password=password)
    conn.bind()

    search_filter = f'(&(objectClass=user)(sAMAccountName={admin[5:]}))'  # Modify this filter as needed
    conn.search(search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['displayName'])

    # Print the found users' sAMAccountName
    for entry in conn.entries:
        return entry.displayName.value
    # Unbind from the server
    conn.unbind()

def get_fullname_u(user):

    from ldap3 import Server, Connection, SUBTREE
    from config.config import server_address, username, password, base_dn

    # Connect to the AD server
    server = Server(server_address)
    conn = Connection(server, user=username, password=password)
    conn.bind()

    search_filter = f'(&(objectClass=user)(sAMAccountName={user}))'  # Modify this filter as needed
    conn.search(search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['displayName'])

    # Print the found users' sAMAccountName
    for entry in conn.entries:
        return entry.displayName.value
    # Unbind from the server
    conn.unbind()

def get_responsible():

    from ldap3 import Server, Connection, SUBTREE
    from config.config import server_address, username, password, base_dn

    # Connect to the AD server
    server = Server(server_address)
    conn = Connection(server, user=username, password=password)
    conn.bind()

    responsible_list = []
    responsible_list.append(' ')
    # Search for users with "admin" in their sAMAccountName
    search_filter = '(&(objectClass=user)(sAMAccountName=admin*))'  # Modify this filter as needed
    conn.search(search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['sAMAccountName'])

    # Print the found users' sAMAccountName
    for entry in conn.entries:
        # sAMAccountName = entry.sAMAccountName.value
        if entry.sAMAccountName.value in blacklist:
            pass

        elif "admin" in entry.sAMAccountName.value:

            # find in ad user that have same username without word "user" and get email
            if entry.sAMAccountName.value == "adminrobkli":
                search_filter = f'(&(objectClass=user)(sAMAccountName=robkliu))'

            else:
                search_filter = f'(&(objectClass=user)(sAMAccountName={entry.sAMAccountName.value[5:]}))'
            conn.search(search_base=base_dn,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=['sAMAccountName', 'name', 'mail'])
            for entry1 in conn.entries:
                username = entry.sAMAccountName.value
                email = entry1.mail.value if 'mail' in entry1 else 'N/A'
                responsible_list.append(entry1.name.value)

    return responsible_list

    # Unbind from the server
    conn.unbind()

def get_office(user):
    office_numbers = set()
    office_numbers.add("")


    # Establish connection
    conn = connect_AD()

    # Search for users with office numbers
    conn.search(base_dn, f'(&(objectClass=user)(sAMAccountName={user}))',
                attributes="physicalDeliveryOfficeName")

    if 'physicalDeliveryOfficeName' in conn.entries[0]:
        result = conn.entries[0]['physicalDeliveryOfficeName']
        conn.unbind()
        return result
    else:
        conn.unbind()
        return None


