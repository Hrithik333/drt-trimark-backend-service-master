from app.model.db import ConnectDB
import jwt
connection = ConnectDB()
mongodb_connection = connection.connect_db()


class UserConfigService:
    def __init__(self):
        pass

    @staticmethod
    def save_user_config(req):
        user_id = req["user_id"]
        use_case = req["use_case"]
        config_name = req["config_name"]
        metrics = req["metrics"]
        filters = req["filters"]
        req_type = req["req_type"]
        from_date = req["from_date"]
        to_date = req["to_date"]
        collections = mongodb_connection.drt_trimark["user_saved_config"]
        record = collections.find_one({"user_id": user_id})
        item = {}
        if record is None:
            item["user_id"] = user_id
            configs = {
                       use_case: {
                                  config_name: {
                                                 "metrics": metrics,
                                                 "filters": filters,
                                                 "req_type": req_type,
                                                 "from_date": from_date,
                                                 "to_date": to_date
                                                 }
                                 }
                       }
            item["configs"] = configs
            collections.insert(item)
            return {"status": "SUCCESS", "message": "Configuration saved successfully."}
        else:
            existing_configs = record["configs"]
            if use_case in existing_configs.keys():
                if config_name in existing_configs[use_case].keys():
                    return {"status": "FAILED", "message": "Configuration name already exists."}
                else:
                    existing_configs[use_case][config_name] = {
                        "metrics": metrics,
                        "filters": filters,
                        "req_type": req_type,
                        "from_date": from_date,
                        "to_date": to_date
                    }
                    newvalues = {"$set": {'configs': existing_configs}}
                    mongodb_connection.drt_trimark["user_saved_config"].update_one({'user_id': user_id},
                                                                                  newvalues)
                    return {"status": "SUCCESS", "message": "Configuration saved successfully."}
            else:
                existing_configs[use_case][config_name] = {
                    "metrics": metrics,
                    "filters": filters,
                    "req_type": req_type,
                    "from_date": from_date,
                    "to_date": to_date
                }
                newvalues = {"$set": {'configs': existing_configs}}
                mongodb_connection.drt_trimark["user_saved_config"].update_one({'user_id': user_id},
                                                                               newvalues)
                return {"status": "SUCCESS", "message": "Configuration saved successfully."}

    @staticmethod
    def get_user_config(req):
        use_case = req["use_case"]
        config_name = req["config_name"]
        user_id = str(req["user_id"])
        collections = mongodb_connection.drt_trimark["user_saved_config"]
        record = collections.find_one({"user_id": user_id})
        if record is None:
            return {"status": "FAILED", "message": "User configuration does not exist."}
        else:
            for i in list(record['configs']):
                if i == use_case:
                    for k in list(record['configs'][i]):
                        if k == config_name:
                            return record["configs"][use_case][config_name]
                    return {"status": "FAILED", "message": "Config name does not exist."}
                else:
                    return {"status": "FAILED", "message": "User case does not exist."}


    @staticmethod
    def delete_saved_user_config(user_id , data):
        use_case = data['use_case']
        config_name = data["config_name"]
        collections = mongodb_connection.drt_trimark["user_saved_config"]
        record = collections.find_one({"user_id": user_id})
        if record is None:
            return {"status": "FAILED", "message": "User configuration does not exist."}
        else:
            for i in list(record['configs']):
                if i == use_case:
                    for k in list(record['configs'][i]):
                        if k == config_name:
                            del record['configs'][i][k]
                            newvalues = {"$set": {'configs': record["configs"]}}
                            mongodb_connection.drt_trimark["user_saved_config"].update_one({'user_id': user_id},newvalues)
                            return {"status": "SUCCESS", "message": "Deleted Successfully"}
                    return {"status": "FAILED", "message": "Config name does not exist."}
                else:
                    return {"status": "FAILED", "message": "User case does not exist."}

    @staticmethod
    def update_saved_user_config(user_id, data):
        use_case = data['use_case']
        config_name = data["config_name"]
        collections = mongodb_connection.drt_trimark["user_saved_config"]
        record = collections.find_one({"user_id": user_id})
        if record is None:
            return {"status": "FAILED", "message": "User configuration does not exist."}
        else:
            for i in list(record['configs']):
                if i == use_case:
                    for k in list(record['configs'][i]):
                        if k == config_name:
                            record['configs'][i][k].update(data['update_body'])
                            newvalues = {"$set": {'configs': record["configs"]}}
                            mongodb_connection.drt_trimark["user_saved_config"].update_one({'user_id': user_id}, newvalues)
                            return {"status": "SUCCESS", "message": "Updated Successfully"}
                    return {"status": "FAILED", "message": "Config name does not exist."}
                else:
                    return {"status": "FAILED", "message": "User case does not exist."}



