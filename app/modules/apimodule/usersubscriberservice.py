import base64
import datetime
import os
import smtplib
import mysql
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from app.modules.fetchdataservice import FetchDataService
import xlsxwriter
from bson.objectid import ObjectId
from app.modules.apimodule.typeconfig import use_case_id, date_selector
from app.model.db import ConnectDB

connection = ConnectDB()
mongodb_connection = connection.connect_db()


class UserSubscriptionService:
    def __init__(self):
        pass

    @staticmethod
    def create_user_subscription(user_id, req):
        use_case = req["use_case"]
        metrics = req["metrics"]
        filters = req["filters"]
        req_type = req["req_type"]
        subscription_name = req["subscription_name"]
        interval = req["interval"]
        email = req["email"]
        mydb = mysql.connector.connect(
            host="ac1aa41ef8c434e959e8dde38ea6dca6-782152459.us-east-1.elb.amazonaws.com",
            user="root",
            password="trimarkdrt",
            database="user_details_database"
        )
        cursor = mydb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_details WHERE id = %s', (user_id,))
        record = cursor.fetchone()
        # collections = mongodb_connection.drt_trimark["user_details"]
        # record = collections.find_one({"_id": user_id})
        if record:
            collections2 = mongodb_connection.drt_trimark["user_subscription"]
            for i in interval:
                item = {'user_id': user_id, 'email': email, 'subscription_name': subscription_name, 'interval': i,
                        'next_email_date': (datetime.datetime.today().date() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                        'previous_email_date': '',
                        "metrics": metrics, 'filter': filters, 'req_type': req_type, 'use_case': use_case}
                collections2.insert_one(item)
            send_from = "anicca.developer@aniccadata.in"
            msg = MIMEMultipart()
            msg['From'] = "anicca.developer@aniccadata.in"
            msg['To'] = email
            msg['Subject'] = "DRT - New Subscription Confirmation"
            msg.attach(MIMEText("Hello,\n\nWe have received your subscription request."
                                "\nThank you for subscribing to DRT Subscription service.\n"
                                "Subscription Name : {}\n\n" \
                                "Thanks and Regards,\n" \
                                "DRT Team\n".format(subscription_name)))
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login("anicca.developer@aniccadata.in", base64.b64decode("QW5pY2NhRGV2QDIx").decode('utf-8'))
            s.sendmail(send_from, email, msg.as_string())
            s.quit()
            return {"message": "Subscription created successfully", "status": "SUCCESS"}
        else:
            return {"message": "Invalid User.", "status": "FAILURE"}

    @staticmethod
    def get_user_subscriptions(user_id, use_case):
        collections = mongodb_connection.drt_trimark["user_subscription"]
        records = collections.find({"user_id": user_id, "use_case": use_case})
        response = []
        for record in records:
            response.append({"Subscription ID": str(record["_id"]), "Email": record["email"], "Last Iteration": record["previous_email_date"],
                             "Next Iteration": record["next_email_date"], "Name": record["subscription_name"], "Actions": True})
        return response

    @staticmethod
    def send_user_subscriptions_email(subscriber_id, user_id):
        collections = mongodb_connection.drt_trimark["user_subscription"]
        record = collections.find_one({"user_id": user_id, "_id": ObjectId(subscriber_id)})
        if record:
            UserSubscriptionService.job(record)
            return {"message": "Email Sent Successfully", "status": "SUCCESS"}
        else:
            return {"message": "Invalid Subscription.", "status": "FAILURE"}

    @staticmethod
    def job(record):
        email = record["email"]
        metrics = record["metrics"]
        filters = record["filter"]
        req_type = record["req_type"]
        use_case = record["use_case"]
        sub_name = record["subscription_name"]
        req = {"date_selector": date_selector[use_case], "req_type": req_type,
               "filters": filters, "metrics": metrics}
        response = FetchDataService.generate_graph_response(req, use_case_id[use_case])
        data = FetchDataService.generate_table_response(response)
        file_name = UserSubscriptionService.generate_excel_from_data(data)
        UserSubscriptionService.send_single_email_user_subscription(email, file_name, sub_name)
        print("Email successfully sent for {} at {}.".format(record["subscription_name"],
                                                             datetime.datetime.now().strftime("%Y%m%d%h%M%s")))

    @staticmethod
    def generate_excel_from_data(data):
        row = 0
        col = 0
        file_name = 'file_{}.xlsx'.format(datetime.datetime.now().strftime("%Y%m%d%h%M%s"))
        for k, v in data.items():
            workbook = xlsxwriter.Workbook(file_name)
            worksheet = workbook.add_worksheet(name=k)
            for i in v:
                worksheet.write(row, col, i["name"])
                col += 1
            col = 0
            for i in v:
                row = 1

                for x in range(len(i["data"])):
                    worksheet.write(row, col, i["data"][row-1])
                    row += 1
                col += 1
        workbook.close()
        return file_name

    @staticmethod
    def send_single_email_user_subscription(email, file_name_to_mail, sub_name):
        send_from = "anicca.developer@aniccadata.in"
        msg = MIMEMultipart()
        msg['From'] = "anicca.developer@aniccadata.in"
        msg['To'] = email
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Digital Reporting Tool - Subscriptions - One Time Email"
        msg.attach(MIMEText("Hi,\nPlease find the attachment below for the subscription {}.\n".format(sub_name)))
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(file_name_to_mail, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="test.xlsx"')
        msg.attach(part)
        smtp = smtplib.SMTP("smtp.gmail.com", 587)
        smtp.starttls()
        smtp.login("anicca.developer@aniccadata.in", base64.b64decode("QW5pY2NhRGV2QDIx").decode('utf-8'))
        smtp.sendmail(send_from, email, msg.as_string())
        smtp.quit()
        os.remove(file_name_to_mail)