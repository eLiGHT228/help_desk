from database.database import User, engine
from integrations.AD import connect_AD
from sqlalchemy.orm import sessionmaker
from config.config import base_dn
import logging
import time


def sync_ldap():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Database session setup
    Session = sessionmaker(bind=engine)
    session = Session()
    while True:
        try:
            # Establish connection
            conn = connect_AD()
            logger.info("Connection done!")

            # Search for users in LDAP
            conn.search(
                base_dn,
                '(&(objectClass=user)(|(givenName=*)(sn=*)))',
                attributes=[
                    'sAMAccountName',
                    'givenName',
                    'sn',
                    'mail',
                    'physicalDeliveryOfficeName',
                    'department',
                    'company'
                ]
            )

            # Track LDAP user IDs
            ldap_user_ids = set()

            # Iterate over search results
            for entry in conn.entries:
                try:
                    logger.info(entry)
                    ad_id = str(entry['sAMAccountName'])
                    ldap_user_ids.add(ad_id)  # Add user ID to the set
                    ad_name = (entry['givenName'].value if 'givenName' in entry else '') + " " + (
                        entry['sn'].value if 'sn' in entry else '')
                    ad_email = entry['mail'].value if 'mail' in entry else None
                    ad_room = entry['physicalDeliveryOfficeName'].value if 'physicalDeliveryOfficeName' in entry else None
                    ad_company = entry['company'].value if 'company' in entry else None
                    ad_department = entry['department'].value if 'department' in entry else None


                    # Check if the user already exists in the database
                    existing_user = session.query(User).filter_by(id=ad_id).first()

                    if ad_email:
                        if existing_user is None:
                            # logger.info("NEW user!")
                            new_user = User(
                                id=str(ad_id),
                                name=str(ad_name),
                                email=str(ad_email),
                                room_nr=str(ad_room),
                                company=str(ad_company),
                                department=str(ad_department),
                                status="active"
                            )
                            # logger.info(f"Adding new user: {new_user.id}")
                            session.add(new_user)
                            session.commit()
                            # logger.info("User added successfully.")
                        else:
                            # logger.info(f"EXISTING user: {existing_user.id}")
                            # Update the existing user details if needed
                            existing_user.name = ad_name
                            existing_user.email = ad_email
                            existing_user.room_nr = ad_room
                            existing_user.company = ad_company
                            existing_user.department = ad_department
                            existing_user.status = "active"
                            session.commit()
                            # logger.info("User details updated successfully.")
                    else:
                        logger.info("User email is None, skipping user.")
                    #
                    # logger.info("=========================================================")

                except Exception as e:
                    # logger.error(f"An error occurred while processing entry {entry}: {e}")
                    session.rollback()  # Rollback in case of error to maintain database integrity

            # Reconciliation step: Identify users in the database not present in LDAP
            db_users = session.query(User).all()
            for db_user in db_users:
                if db_user.id not in ldap_user_ids:
                    # User is in the database but not in LDAP, so remove or deactivate the user
                    # logger.info(f"User {db_user.id} not found in LDAP, disabling user")
                    db_user.status = "disabled"
                    session.commit()
                    # logger.info(f"User {db_user.id} disabled successfully.")

        except Exception as e:
            logger.error(f"An error occurred: {e}")

        finally:
            # Unbind the LDAP connection
            if conn:
                conn.unbind()
            # Close the database session
            session.close()
        time.sleep(60)
