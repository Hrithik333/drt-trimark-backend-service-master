import csv

from app.model.db import ConnectDB

from datetime import datetime


class inputFromCsv:

    def __init__(self):
        pass

    @staticmethod
    def standardized_sales_order_detail():
        connection = ConnectDB()
        mongodb_connection = connection.connect_db()
        collections = mongodb_connection.drt_trimark["use_case_filters"]
        use_case_filters = collections.find_one({'use_case_id': int(1)})
        collections = mongodb_connection.drt_trimark["use_case_metrics"]
        use_case_metrics = collections.find_one({'use_case_id': int(1)})
        with open("C:/Users/umesh/Downloads/standardized_sales_order_detail.csv", encoding='utf-8') as file:
            csvreader = csv.reader(file)
            header = next(csvreader, None)  # skip the headers
            values = []
            for row in csvreader:
                item = {}
                for element in use_case_filters['filters']:
                    item[element['db_name']] = row[header.index(element['db_name'])].strip()
                    if element['db_name'] == "company_cd" or element['db_name'] == "cost_center_cd" or element[
                        'db_name'] == "tax_amount" or element['db_name'] == "product_unit_cost" or element[
                        'db_name'] == "product_extended_cost" or element['db_name'] == "product_landed_cost" or element[
                        'db_name'] == "product_average_cost" or element['db_name'] == "product_accounting_cost" or \
                            element['db_name'] == "product_po_cost" or element['db_name'] == "product_total_price" or \
                            element['db_name'] == "invoice_quantity" or element['db_name'] == "shipped_quantity" or \
                            element['db_name'] == "backorder_quantity":
                        try:
                            item[element['db_name']] = float(item[element['db_name']])
                        except:
                            item[element['db_name']] = float(0)

                    if element['db_name'] == "order_created_date":
                        item[element['db_name']] = datetime.strptime(item[element['db_name']], '%y/%m/%d')
                    if item[element['db_name']] == "":
                        item[element['db_name']] = "NULL"
                    if item[element['db_name']] not in element['filter_values']:
                        element['filter_values'].append(item[element['db_name']])
                        newvalues = {"$set": {'filters': use_case_filters['filters']}}
                        mongodb_connection.drt_trimark["use_case_filters"].update_one({'use_case_id': int(1)},
                                                                                      newvalues)
                for element in use_case_metrics['metrics']:
                    item[element['db_name']] = row[header.index(element['db_name'])].strip()
                    if element['db_name'] == "company_cd" or element['db_name'] == "cost_center_cd" or element[
                        'db_name'] == "tax_amount" or element['db_name'] == "product_unit_cost" or element[
                        'db_name'] == "product_extended_cost" or element['db_name'] == "product_landed_cost" or element[
                        'db_name'] == "product_average_cost" or element['db_name'] == "product_accounting_cost" or \
                            element['db_name'] == "product_po_cost" or element['db_name'] == "product_total_price" or \
                            element['db_name'] == "invoice_quantity" or element['db_name'] == "shipped_quantity" or \
                            element['db_name'] == "backorder_quantity":
                        try:
                            item[element['db_name']] = float(item[element['db_name']])
                        except:
                            item[element['db_name']] = float(0)

                    if item[element['db_name']] == "":
                        item[element['db_name']] = "NULL"

                item['order_created_date'] = row[header.index('order_created_date')].strip()
                item['order_created_date'] = datetime.strptime(item['order_created_date'], '%Y-%m-%d')

                values.append(item)
                if values.__len__() > 100:
                    collections = mongodb_connection.drt_trimark["standardized_sales_order_detail"]
                    collections.insert_many(values)
                    values = []
            if values.__len__() > 0:
                collections = mongodb_connection.drt_trimark["standardized_sales_order_detail"]
                collections.insert_many(values)

        return "Data inserted", 200

    @staticmethod
    def standardized_purchase_order_detail():
        connection = ConnectDB()
        mongodb_connection = connection.connect_db()
        collections = mongodb_connection.drt_trimark["use_case_filters"]
        use_case_filters = collections.find_one({'use_case_id': int(2)})
        collections = mongodb_connection.drt_trimark["use_case_metrics"]
        use_case_metrics = collections.find_one({'use_case_id': int(2)})
        with open("C:\SampleData\standardized_purchase_order_detail.csv", encoding='utf-8') as file:
            csvreader = csv.reader(file)
            header = next(csvreader, None)  # skip the headers
            values = []
            for row in csvreader:
                item = {}
                for element in use_case_filters['filters']:
                    item[element['db_name']] = row[header.index(element['db_name'])].strip()
                    if element['db_name'] == "company_cd" or element['db_name'] == "cost_center_cd" or element[
                        'db_name'] == "received_quanity" or element['db_name'] == "vouchered_quantity" or element[
                        'db_name'] == "unit_price" or element['db_name'] == "extended_price" or element[
                        'db_name'] == "freight_amount":
                        try:
                            item[element['db_name']] = float(item[element['db_name']])
                        except:
                            item[element['db_name']] = float(0)
                    if item[element['db_name']] == "":
                        item[element['db_name']] = "NULL"
                    if item[element['db_name']] not in element['filter_values']:
                        element['filter_values'].append(item[element['db_name']])
                        newvalues = {"$set": {'filters': use_case_filters['filters']}}
                        mongodb_connection.drt_trimark["use_case_filters"].update_one({'use_case_id': int(2)},
                                                                                      newvalues)
                for element in use_case_metrics['metrics']:
                    item[element['db_name']] = row[header.index(element['db_name'])].strip()
                    if element['db_name'] == "company_cd" or element['db_name'] == "cost_center_cd" or element[
                        'db_name'] == "received_quanity" or element['db_name'] == "vouchered_quantity" or element[
                        'db_name'] == "unit_price" or element['db_name'] == "extended_price" or element[
                        'db_name'] == "freight_amount":
                        try:
                            item[element['db_name']] = float(item[element['db_name']])
                        except:
                            item[element['db_name']] = float(0)

                    if item[element['db_name']] == "":
                        item[element['db_name']] = "NULL"
                item['po_created_dt'] = row[header.index('po_created_dt')].strip()
                try:
                    item['po_created_dt'] = datetime.strptime(item['po_created_dt'], '%d-%m-%Y')
                except:
                    item['po_created_dt'] = datetime.strptime(item['po_created_dt'], '%Y-%m-%d')

                values.append(item)
                if values.__len__() > 100:
                    collections = mongodb_connection.drt_trimark["standardized_purchase_order_detail"]
                    collections.insert_many(values)
                    values = []
            if values.__len__() > 0:
                collections = mongodb_connection.drt_trimark["standardized_purchase_order_detail"]
                collections.insert_many(values)

        return "Data inserted", 200
