from app.model.db import ConnectDB

connection = ConnectDB()
mongodb_connection = connection.connect_db()


class FilterValuesService:
    def __init__(self):
        pass

    @staticmethod
    def get_filter_values(use_case_id, name, query):
        collections = mongodb_connection.drt_trimark["use_case_filters"]
        record = collections.find_one({"use_case_id": use_case_id})
        filters = record["filters"]
        filter_values = list(filter(lambda x: x["db_name"] == name, filters))[0]["filter_values"]
        if query is None or query == "":
            if len(filter_values) <= 20:
                return filter_values
            else:
                return filter_values[:20]
        else:
            filtered_values = list(s for s in filter_values if str(query).lower() in str(s).lower())
            if len(filtered_values) <= 20:
                return filtered_values
            else:
                return filtered_values[:20]
