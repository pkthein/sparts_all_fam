
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
        print(output, "@36 api")
        if output:
            return output
        return category_cli.api_test()
    except Exception as e:
        return e

@app.route("/phyo/cat", methods=["GET"])
def list_category():
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    
    try:
        output = category_cli.api_do_list_category(config)
        
        if output:
            return output
        return category_cli.api_test()
    except Exception as e:
        return e
    

@app.route("/phyo/test", methods=["POST"])
def testing_():
    try:
        # if not request.json or "category" not in request.json:
        #     return "Error"
        data = json.dumps(request.json["private_key"])
        
        # return json.loads(data)
        return (request.json["category"]["uuid"] + request.json["category"]["name"])
    except Exception as e:
        return e
    
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
