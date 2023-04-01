import datetime
from dateutil.relativedelta import relativedelta

from app.model.db import ConnectDB

connection = ConnectDB()
mongodb_connection = connection.connect_db()


class FetchDataService:
    def __init__(self):
        pass

    @staticmethod
    def generate_graph_response(req, use_case_id):
        date_selector = req["date_selector"]
        req_type = req["req_type"]
        from_date, to_date, views = FetchDataService.get_date_range_and_views(req, req_type)
        date_filter = {date_selector: {'$gte': from_date, '$lte': to_date}}
        filters = req["filters"]
        filters_dict = {}
        for filter_name, values in filters.items():
            filters_dict[filter_name] = {'$in': values}

        response = {}
        for view in views:
            format = None
            format = FetchDataService.get_format_wrt_view(format, view)
            metrics, results = FetchDataService.get_aggregation_data(date_filter, filters_dict, format, req,
                                                                     use_case_id)
            data_dict = {}
            dates = FetchDataService.getDateKeys(view, from_date, to_date)
            for metric in metrics:
                dict1 = {}
                for date in dates:
                    dict1[date] = 0
                data_dict[metric] = dict1

            for item in results:
                key = item["_id"]
                del item["_id"]
                for k, v in item.items():
                    if v is not None:
                        if k in data_dict.keys():
                            data_dict[k][key] = round(v, 2)
                        else:
                            data_dict[k] = {key: round(v, 2)}
            x_label = FetchDataService.get_x_label(view)
            for u, v in data_dict.items():
                metric_display_names = FetchDataService.metrics(use_case_id)
                if u not in response:
                    response[u] = {"display_name": metric_display_names[u],
                                   "metric_response": {
                                       view: {"data": FetchDataService.rename_labels(v, x_label),
                                              "x-label": x_label,
                                              "y-label": "Avg. {}".format(metric_display_names[u])}}}
                else:
                    response[u]["metric_response"][view] = {"data": FetchDataService.rename_labels(v, x_label),
                                                            "x-label": x_label,
                                                            "y-label": "Avg. {}".format(metric_display_names[u])}
        return response

    @staticmethod
    def rename_labels(dict1, x_label):
        if x_label == "Month":
            new_dict = {}
            month = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "June", 7: "July", 8: "Aug", 9: "Sep",
                     10: "Oct", 11: "Nov", 12: "Dec"}
            for x, y in dict1.items():
                labels = x.split("-")
                new_key = labels[0] + " " + month[int(labels[1])]
                new_dict[new_key] = y
            return new_dict
        if x_label == "Week No.":
            new_dict = {}
            for x, y in dict1.items():
                labels = x.split("-")
                new_key = labels[0] + " Week " + (labels[1])
                new_dict[new_key] = y
            return new_dict
        if x_label == "Date":
            return dict1

    @staticmethod
    def get_aggregation_data(date_filter, filters_dict, format, req, use_case_id):
        """
        Apply the aggregation filters and metrics to the mongo executor and return the response
        :param date_filter:
        :param filters_dict:
        :param format:
        :param req:
        :return:
        """
        use_case_filters_filter = {"id": str(use_case_id)}
        collections = mongodb_connection.drt_trimark["use_cases"]
        record = collections.find_one(use_case_filters_filter)
        db_collection_name = record["collection_name"]
        dict1 = {'_id': {'$dateToString': {'format': format, 'date': "${}".format(req["date_selector"])}}}
        metrics_dict = {}
        metrics = req["metrics"]
        for metric in metrics:
            metrics_dict[metric] = {'$avg': "${}".format(metric)}
        select_by_date = {"$match": date_filter}
        for key, value in filters_dict.items():
            date_filter[key] = value
        for key, value in metrics_dict.items():
            dict1[key] = value
        separate_by_date_avg = {'$group': dict1}
        pipeline = [
            select_by_date,
            separate_by_date_avg
        ]
        collections = mongodb_connection.drt_trimark[db_collection_name]
        results = collections.aggregate(pipeline)
        return metrics, results

    @staticmethod
    def get_x_label(view):
        """
        Get the label for x-axis to be displayed on the UI
        :param view:
        :return:
        """
        if view == "Daily":
            xlabel = "Date"
        if view == "Weekly":
            xlabel = "Week No."
        if view == "Monthly":
            xlabel = "Month"
        return xlabel

    @staticmethod
    def get_format_wrt_view(query_format, view):
        """
        Get the format for the aggregation to run on the mongo query executor
        :param query_format:
        :param view:
        :return:
        """
        if view == "Daily":
            query_format = '%Y-%m-%d'
        elif view == "Weekly":
            query_format = '%Y-%U'
        elif view == "Monthly":
            query_format = '%Y-%m'
        return query_format

    @staticmethod
    def get_date_range_and_views(req, req_type):
        """
        Return the date ranges and respective views to be displayed on the UI
        :param req:
        :param req_type:
        :return:
        """
        if req_type == "date_range":
            from_date = req["from_date"]
            to_date = req["to_date"]
            from_date = datetime.datetime.strptime(from_date, '%Y-%m-%d')
            to_date = datetime.datetime.strptime(to_date, '%Y-%m-%d')
            views = FetchDataService.get_date_range_views(from_date, to_date)
        else:
            if req_type == "previous_week":
                to_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                from_date = to_date - datetime.timedelta(days=7)
                views = ["Daily"]
            elif req_type == "previous_month":
                to_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                from_date = to_date - relativedelta(months=1)
                views = ["Weekly"]
            elif req_type == "previous_year":
                to_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
                from_date = to_date - datetime.timedelta(days=365)
                views = ["Monthly"]
        return from_date, to_date, views

    @staticmethod
    def get_date_range_views(from_date, to_date):
        days = to_date - from_date
        number_of_days = days.days
        views = []
        if number_of_days <= 7:
            views.append("Daily")
        elif 7 < number_of_days <= 30:
            views.append("Daily")
            views.append("Weekly")
        else:
            views.append("Monthly")
        return views

    @staticmethod
    def metrics(use_case_id):
        """
        Get the metrics respective db_names and display names
        :return:
        """

        collections = mongodb_connection.drt_trimark["use_case_metrics"]
        records = collections.find_one({'use_case_id': use_case_id})
        metrics = records["metrics"]
        response = {}
        for metric in metrics:
            response[metric["db_name"]] = metric["display_name"]
        return response

    @staticmethod
    def getDateKeys(view, from_date, to_date):
        if view == "Daily":
            keys = []
            from_day = from_date.date()
            to_day = to_date.date()
            for i in range((to_day - from_day).days + 1):
                day = (from_day + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                if day not in keys:
                    keys.append(day)
            return keys
        elif view == "Weekly":
            keys = []
            for i in range((to_date - from_date).days + 1):
                d = (from_date + datetime.timedelta(days=i)).isocalendar()[:2]  # e.g. (2011, 52)
                keys.append('{}-{:02}'.format(*d))
            return sorted(set(keys))
        elif view == "Monthly":
            keys = []
            while from_date < to_date:
                keys.append(from_date.strftime("%Y-%m"))
                from_date += relativedelta(months=1)
            return keys

    @staticmethod
    def generate_table_response(data):
        response = {}
        response1 = {}
        if len(list(list(data.values())[0]['metric_response'].keys())) > 1:
            key1 = list(list(data.values())[0]['metric_response'].keys())[0]
            response[key1] = {}
            for key in list(list(list(data.values())[0]['metric_response'].values())[0]["data"].keys()):
                response1[key] = {}
                response[key1][key] = {}
            key2 = list(list(data.values())[0]['metric_response'].keys())[1]
            response[key2] = {}
            for key in list(list(list(data.values())[0]['metric_response'].values())[1]["data"].keys()):
                response1[key] = {}
                response[key2][key] = {}

            for item in data:
                for value in data[item]['metric_response'].values():
                    for value1 in value['data']:
                        if value1 not in response1:
                            if value1[4] == '-':
                                response[key1][value1] = {}
                                response1[value1] = {}
                            else:
                                response[key2][value1] = {}
                                response1[value1] = {}
                        else:
                            if value1[4] == '-':
                                response1[value1][data[item]['display_name']] = value['data'][value1]
                                response[key1][value1][data[item]['display_name']] = response1[value1][
                                    data[item]['display_name']]
                            else:
                                response1[value1][data[item]['display_name']] = value['data'][value1]
                                response[key2][value1][data[item]['display_name']] = response1[value1][
                                    data[item]['display_name']]

        else:
            key1 = list(list(data.values())[0]['metric_response'].keys())[0]
            response[key1] = {}
            for key in list(list(list(data.values())[0]['metric_response'].values())[0]["data"].keys()):
                response1[key] = {}
                response[key1][key] = {}

            for item in data:
                for value in data[item]['metric_response'].values():
                    for value1 in value['data']:
                        if value1 not in response1:
                            response1[value1] = {}
                        else:
                            response1[value1][data[item]['display_name']] = value['data'][value1]
                            response[key1][value1][data[item]['display_name']] = response1[value1][
                                data[item]['display_name']]

        final_response = {}

        for k, v in response.items():
            res = {"Time Axis": []}
            for i, j in v.items():
                res["Time Axis"].append(i)
                for a, b in j.items():
                    if a not in res:
                        res[a] = []
                    res[a].append(b)
            final_response[k] = res

        for k, v in final_response.items():
            count = 0
            formatted_res = []
            for i, j in v.items():
                count += 1
                formatted_res.append({"name": i, "data": j})
            final_response[k] = formatted_res
        return final_response
