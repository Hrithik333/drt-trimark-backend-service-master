from app.model.db import ConnectDB

connection = ConnectDB()
mongodb_connection = connection.connect_db()


class FiltersService:
    def __init__(self):
        pass

    @staticmethod
    def getSalesOrderFilterAndMetrics():
        use_case_name = "Standardized Sales Order"
        return FiltersService.get_filters_and_metrics(use_case_name)

    @staticmethod
    def getPurchaseOrderFilterAndMetrics():
        use_case_name = "Standardized Purchase Order"
        return FiltersService.get_filters_and_metrics(use_case_name)

    @staticmethod
    def get_filters_and_metrics(use_case_name):
        response = {}
        sales_order_filter = {"name": use_case_name}
        collections = mongodb_connection.drt_trimark["use_cases"]
        sales_order_use_case = collections.find_one(sales_order_filter)
        id = sales_order_use_case["id"]
        use_case_filters_filter = {"use_case_id": int(id)}
        collections = mongodb_connection.drt_trimark["use_case_filters"]
        filters = collections.find_one(use_case_filters_filter)
        #del filters["_id"]
        #del filters["use_case_id"]
        collections = mongodb_connection.drt_trimark["use_case_metrics"]
        metrics = collections.find_one(use_case_filters_filter)
        del metrics["_id"]
        del metrics["use_case_id"]
        for filter in filters["filters"]:
            del filter["filter_values"]
        response["filters"] = filters["filters"]
        response["date_selector"] = filters["date_selector"]
        response["metrics"] = metrics["metrics"]
        return response
