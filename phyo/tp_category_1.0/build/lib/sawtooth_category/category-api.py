
# copyright 2017 Wind River Systems
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from flask import Flask, jsonify, make_response, request, json
import category_cli
import configparser

app = Flask(__name__)

@app.route("/phyo/ping", methods=["GET"])
def get_ping_result():
    
    output = ret_msg("success","OK","EmptyRecord","phyo is here")
    return output 

@app.route("/phyo/cat", methods=["POST"])
def create_category():
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        
        output = category_cli.api_do_create_category(request.json, config)    
        
        return output
    except Exception as e:
        return e

@app.route("/phyo/cat/amend", methods=["POST"])
def amend_category():
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        
        output = category_cli.api_do_amend_category(request.json, config)    
        
        return output
    except Exception as e:
        return e

@app.route("/phyo/cat", methods=["GET"])
def list_category():
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        output = category_cli.api_do_list_category(config)
        
        return output
    except Exception as e:
        return e
        
@app.route("/phyo/cat/<string:category_id>", methods=["GET"])
def retreive_category(category_id):
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        output = category_cli.api_do_retrieve_category(category_id, config)
        
        return output
    except Exception as e:
        return e

@app.route("/phyo/cat/history/<string:category_id>", methods=["GET"])
def retreive_category_history(category_id):
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        output = category_cli.api_do_retrieve_category(
                        category_id, config, all_flag=True
                    )
        return output
    except Exception as e:
        return e
        
@app.route(
    "/phyo/cat/<string:category_id>/date/<string:START>",
    methods=["GET"]
)
def retreive_category_history_date(category_id, START):
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        output = category_cli.api_do_retrieve_category(
                        category_id, config, range_flag=[START, START]
                    )
        print(output)
        return output
    except Exception as e:
        return e
################################################################################
#                                   TEST                                       #
################################################################################
@app.route("/phyo/test", methods=["POST"])
def testing_():
    try:
        # if not request.json or "category" not in request.json:
        #     return "Error"
        # data = json.dumps(request.json["private_key"])
        
        # return json.loads(data)
        # return (request.json["category"]["uuid"] + request.json["category"]["name"])
        return json.dumps(request.json)
    except Exception as e:
        return e

@app.route("/phyo/test", methods=["GET"])
def testing_get():
    try:
        # if not request.json or "category" not in request.json:
        #     return "Error"
        # data = json.dumps(request.json["private_key"])
        
        # return json.loads(data)
        # return (request.json["category"]["uuid"] + request.json["category"]["name"])
        return "phyo test get was called successfully"
    except Exception as e:
        return e
################################################################################
#                                                                              #
################################################################################
def ret_msg(status, message, result_type, result):
    msgJSON = "{}"
    key = json.loads(msgJSON)
    key["status"] = status
    key["message"] = message
    key["result_type"] = result_type
    key["result"] = result
    msgJSON = json.dumps(key)
    return msgJSON
################################################################################
#                                   MAIN                                       #
################################################################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="850")
################################################################################
#                                                                              #
################################################################################
