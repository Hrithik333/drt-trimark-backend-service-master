import json

from pymongo import MongoClient

from app import app
from flask import jsonify, request

from app.model.db import token_required
from app.modules.apimodule.fetchdataservice import FetchDataService
from app.modules.apimodule.userconfigservice import UserConfigService
from app.modules.apimodule.usersubscriberservice import UserSubscriptionService
from app.modules.apimodule.userservice import UserService
from app.modules.importmodule.inputFromCsv import inputFromCsv
from app.modules.apimodule.filtersservice import FiltersService
from app.modules.apimodule.filtervaluesservice import FilterValuesService
import jwt
sales_order_response = FiltersService.getSalesOrderFilterAndMetrics()
purchase_order_response = FiltersService.getPurchaseOrderFilterAndMetrics()
connection = MongoClient("mongodb+srv://DRT:<password>@cluster0.c8jw4u9.mongodb.net/test")


@app.route("/", methods=["GET"])
def index():
    return "Trimark DRT system"


@app.route("/standardizedSalesOrderDetailCSV", methods=["POST"])
def pos_inbound():
    inputFromCsv.standardized_sales_order_detail()
    return jsonify({"Response": "Data inserted"})


@app.route("/standardizedPurchaseOrderDetailCSV", methods=["POST"])
def standardizedPurchaseOrder():
    inputFromCsv.standardized_purchase_order_detail()
    return jsonify({"Response": "Data inserted"})


@app.route("/getSalesOrdersFiltersAndMetrics", methods=["GET"])
@token_required
def getSalesOrdersFiltersAndMetrics(req):
    return jsonify(sales_order_response)


@app.route("/getPurchaseOrdersFiltersAndMetrics", methods=["GET"])
@token_required
def getPurchaseOrdersFiltersAndMetrics(req):
    return purchase_order_response
    # return jsonify(purchase_order_response)


#@app.route("/register", methods=["POST"])
#def register():
#    req = json.loads(request.data)
#    res = UserService.register(req)
#    return jsonify(res)


#@app.route("/login", methods=["POST"])
#def login():
#    req = json.loads(request.data)
#    res = UserService.login(req)
#    return jsonify(res)


@app.route("/getUseCases", methods = ["GET"])
@token_required
def getUseCases(req):
    collections = connection.drt_trimark["use_cases"]
    docs = collections.find()
    access = []
    for record in docs:
        access.append({"use_case_id": record["id"], "use_case_name": record["name"]})
    return jsonify(access)


@app.route("/fetchSalesOrderData", methods=["POST"])
@token_required
def fetchSalesOrderData(req):
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 1)
    response = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/fetchSalesOrderData/v2", methods=["POST"])
@token_required
def fetchSalesOrderDataV2(req):
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 1)
    req_response = FetchDataService.generate_table_response(response, 1)
    req_response = app.response_class(
        response=json.dumps(req_response),
        status=200,
        mimetype='application/json'
    )
    return req_response


@app.route("/fetchSalesOrderData/v3", methods=["POST"])
@token_required
def fetchSalesOrderDatav3(req):
    api_response = {}
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 1)
    api_response["Graph"] = response
    req_response = FetchDataService.generate_table_response(response)
    api_response["Table"] = req_response
    api_response = app.response_class(
        response=json.dumps(api_response),
        status=200,
        mimetype='application/json'
    )
    return api_response


@app.route("/fetchPurchaseOrderData/v2", methods=["POST"])
@token_required
def fetchPurchaseOrderDataV2(req):
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 2)
    req_response = FetchDataService.generate_table_response(response, 2)
    req_response = app.response_class(
        response=json.dumps(req_response),
        status=200,
        mimetype='application/json'
    )
    return req_response


@app.route("/fetchPurchaseOrderData/v3", methods=["POST"])
@token_required
def fetchPurchaseOrderDatav3(req):
    api_response = {}
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 2)
    api_response["Graph"] = response
    req_response = FetchDataService.generate_table_response(response)
    api_response["Table"] = req_response
    api_response = app.response_class(
        response=json.dumps(api_response),
        status=200,
        mimetype='application/json'
    )
    return api_response


@app.route("/fetchPurchaseOrderData", methods=["POST"])
@token_required
def fetchPurchaseOrderData(req):
    req = json.loads(request.data)
    response = FetchDataService.generate_graph_response(req, 2)
    response = app.response_class(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/save_user_config", methods=["POST"])
@token_required
def save_user_config(req):
    req = json.loads(request.data)
    response = UserConfigService.save_user_config(req)
    return jsonify(response)


@app.route("/get_user_config", methods=["POST"])
@token_required
def get_user_config(req):
    req = json.loads(request.data)
    response = UserConfigService.get_user_config(req)
    return jsonify(response)


@app.route("/get_saved_user_config", methods=["GET"])
@token_required
def get_saved_user_config(req):
    jwt_token = request.headers['x-access-tokens']
    response = UserService.get_saved_user_config(jwt_token)
    return jsonify(response)


@app.route("/salesOrderFilter", methods=["GET"])
@token_required
def salesOrderFilter(req):
    filter_name = request.args["name"]
    query = request.args["query"]
    response = FilterValuesService.get_filter_values(1, filter_name, query)
    return jsonify(response)


@app.route("/purchaseOrderFilter", methods=["GET"])
@token_required
def purchaseOrderFilter(req):
    filter_name = request.args["name"]
    query = request.args["query"]
    response = FilterValuesService.get_filter_values(2, filter_name, query)
    return jsonify(response)


@app.route("/delete_saved_user_config", methods=["POST"])
@token_required
def delete_saved_user_config(req):
    jwt_token = request.headers['x-access-tokens']
    data = request.json
    data1 = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
    user_id = data1["public_id"]
    response1 = UserConfigService.delete_saved_user_config(user_id , data)
    return jsonify(response1)


@app.route("/update_saved_user_config", methods=["POST"])
@token_required
def update_saved_user_config(req):
    jwt_token = request.headers['x-access-tokens']
    data = request.json
    data1 = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
    user_id = data1["public_id"]
    response1 = UserConfigService.update_saved_user_config(user_id , data)
    return jsonify(response1)


@app.route("/create_user_subscription", methods=["POST"])
@token_required
def create_user_subscription(req):
    jwt_token = request.headers['x-access-tokens']
    data = request.json
    data1 = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
    user_id = data1["public_id"]
    response = UserSubscriptionService.create_user_subscription(user_id, data)
    return jsonify(response)


@app.route("/get_user_subscriptions", methods=["GET"])
@token_required
def get_user_subscription(req):
    jwt_token = request.headers['x-access-tokens']
    data1 = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
    user_id = data1["public_id"]
    use_case = request.args["use_case"]
    response = UserSubscriptionService.get_user_subscriptions(user_id, use_case)
    return jsonify(response)


@app.route("/send_user_subscriptions_email", methods=["POST"])
@token_required
def send_user_subscriptions_email(req):
    jwt_token = request.headers['x-access-tokens']
    data1 = jwt.decode(jwt_token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
    user_id = data1["public_id"]
    response = UserSubscriptionService.send_user_subscriptions_email(request.args['subscription_id'], user_id)
    return jsonify(response)