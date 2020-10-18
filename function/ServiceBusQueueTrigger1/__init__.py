import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    connection = psycopg2.connect(user = "udacity@uda-postgresql",
                                  password = "MyPostgresPass",
                                  host = "uda-postgresql.postgres.database.azure.com",
                                  port = "5432",
                                  database = "techconfdb")
    cursor = connection.cursor()

    try:
        notification_query = '''SELECT subject, message 
                                FROM Notification
                                WHERE id = %s;'''

        cursor.execute(notification_query, (notification_id,))
        notification = cursor.fetchone()

        subject = notification[0]
        message = notification[1]
        
        attendees_query = 'SELECT first_name, email FROM Attendee;'
        cursor.execute(attendees_query)
        attendees = cursor.fetchall() 
   
        for attendee in attendees:
            first_name = attendee[0]
            email = attendee[1]
            custom_subject = '{}: {}'.format(first_name, subject)
            # send_email(email, custom_subject, message)

        completed_date = datetime.utcnow()
        status = 'Notified {} attendees'.format(len(attendees))

        notification_update_query = '''UPDATE Notification 
                                SET completed_date = %s, status = %s 
                                WHERE id = %s;'''
        cursor.execute(notification_update_query, (completed_date, status, notification_id))
        connection.commit()
        count = cursor.rowcount
        print(count, "Record Updated successfully ")

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
    #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")



# def send_email(email, subject, body):
#     if not app.config.get('SENDGRID_API_KEY'):
#         message = Mail(
#             from_email=app.config.get('ADMIN_EMAIL_ADDRESS'),
#             to_emails=email,
#             subject=subject,
#             plain_text_content=body)

#         sg = SendGridAPIClient(app.config.get('SENDGRID_API_KEY'))
#         sg.send(message)
