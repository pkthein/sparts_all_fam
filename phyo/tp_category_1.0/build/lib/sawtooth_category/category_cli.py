# Copyright 2017 Intel Corporation
# Copyright 2017 Wind River
#
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
################################################################################
#                               LIBS & DEPS                                    #
################################################################################
from __future__ import print_function

import argparse
import configparser
import getpass
import logging
import os
import traceback
import sys
import shutil
import pkg_resources
import requests
import json

from colorlog import ColoredFormatter

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_category.category_batch import CategoryBatch
from sawtooth_category.exceptions import CategoryException


DISTRIBUTION_NAME = "sawtooth-category"
################################################################################
def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))
################################################################################
#                                   OBJ                                        #
################################################################################
def add_create_parser(subparsers, parent_parser):
    parser = subparsers.add_parser("create", parents=[parent_parser])

    parser.add_argument(
        "category_id",
        type=str,
        help="category identifier")
    
    parser.add_argument(
        "category_name",
        type=str,
        help="Provide category name")
    
    parser.add_argument(
        "description",
        type=str,
        help="provide description")
      
    parser.add_argument(
        "private_key",
        type=str,
        help="Provide User Private Key")
    
    parser.add_argument(
        "public_key",
        type=str,
        help="Provide User Public Key")
    
    parser.add_argument(
        "--disable-client-validation",
        action="store_true",
        default=False,
        help="disable client validation")

def add_list_category_parser(subparsers, parent_parser):
    subparsers.add_parser("list-category", parents=[parent_parser])

def add_retrieve_category_parser(subparsers, parent_parser):
    parser = subparsers.add_parser("retrieve", parents=[parent_parser])

    parser.add_argument(
        "category_id",
        type=str,
        help="an identifier for the category")
        
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        default=False,
        help="show history of uuid")
        
    parser.add_argument(
        "--range",
        nargs=2,
        metavar=("START", "END"),
        default=None,
        help="show history of uuid within the range; FORMAT : yyyymmdd")

def add_update_category_parser(subparsers, parent_parser):
    parser = subparsers.add_parser("update", parents=[parent_parser])

    parser.add_argument(
        "category_id",
        type=str,
        help="an identifier for the category")
        
    parser.add_argument(
        "category_name",
        type=str,
        help="Provide category name")
    
    parser.add_argument(
        "description",
        type=str,
        help="provide description")
      
    parser.add_argument(
        "private_key",
        type=str,
        help="Provide User Private Key")
    
    parser.add_argument(
        "public_key",
        type=str,
        help="Provide User Public Key")
    
    parser.add_argument(
        "--disable-client-validation",
        action="store_true",
        default=False,
        help="disable client validation")

def create_parent_parser(prog_name):
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)
    parent_parser.add_argument(
        "-v", "--verbose",
        action="count",
        help="enable more verbose output")

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = "UNKNOWN"

    parent_parser.add_argument(
        "-V", "--version",
        action="version",
        version=(DISTRIBUTION_NAME + " (Hyperledger Sawtooth) version {}")
        .format(version),
        help="print version information this is modded")

    return parent_parser

def create_parser(prog_name):
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter)

    subparsers = parser.add_subparsers(title="subcommands", dest="command")

    add_create_parser(subparsers, parent_parser)
    add_list_category_parser(subparsers, parent_parser)
    add_retrieve_category_parser(subparsers, parent_parser)
    add_update_category_parser(subparsers, parent_parser)
    
    return parser
################################################################################
#                               FUNCTIONS                                      #
################################################################################
def do_list_category(args, config):
    b_url = config.get("DEFAULT", "url")
  
    client = CategoryBatch(base_url=b_url)

    category_list = client.list_category()

    if category_list is not None:
        
        if str(category_list) != "[]":
            result = ("[" + str(category_list)[3:-2] + "]").replace("b'", "")\
                        .replace("'", "")
            result = json.loads(result)
            result.sort(key=lambda x:x["timestamp"], reverse=True)
            result = json.dumps(result)
            
            output = ret_msg("success", "OK", "ListOf:CategoryRecord", result)
        else:
            output = ret_msg("success", "OK", "ListOf:CategoryRecord", 
                        str(category_list))
        print (output)
    else:
        raise CategoryException("Could not retrieve category listing.")

def do_retrieve_category(args, config):
    all_flag = args.all
    range_flag = args.range
    
    category_id = args.category_id
    
    if range_flag != None:
        all_flag = True
    
    b_url = config.get("DEFAULT", "url")
    client = CategoryBatch(base_url=b_url)
    data = client.retreive_category(category_id, all_flag, range_flag)
    
    if data is not None:
        
        if all_flag == False:
            output = ret_msg("success", "OK", "CategoryRecord", data.decode())
        else:
            output = ret_msg("success", "OK", "CategoryRecord", json.loads(data))
            
        print(output)
    else:
        raise CategoryException("Category not found: {}".format(category_id))
        
def do_create_category(args, config):
    category_id = args.category_id
    category_name = args.category_name
    description = args.description
    private_key = args.private_key
    public_key = args.public_key

    payload = "{}"
    key = json.loads(payload)
    key["publickey"] = public_key
    key["privatekey"] = private_key
    key["allowedrole"] = [{"role":"admin"}, {"role":"member"}]
    payload = json.dumps(key)
    
    headers = {"content-type": "application/json"}
    response = requests.post("http://127.0.0.1:818/api/sparts/ledger/auth", 
                    data=json.dumps(key), headers=headers)
    output = response.content.decode("utf-8").strip()
    statusinfo = json.loads(output)
       
    if statusinfo.get("status") and statusinfo.get("message"):
            
        status = statusinfo["status"]
        message = statusinfo["message"]
            
        if status == "success" and message == "authorized":
            
            b_url = config.get("DEFAULT", "url")
            client = CategoryBatch(base_url=b_url)
            response = client.create_category(category_id, category_name, 
                            description, private_key, public_key)
            print_msg(response)
            
        else:
            print(output)
    else:
        print(output)
   
def do_update_category(args, config):
    category_id = args.category_id
    category_name = args.category_name
    description = args.description
    private_key = args.private_key
    public_key = args.public_key
    
    payload = "{}"
    key = json.loads(payload)
    key["publickey"] = public_key
    key["privatekey"] = private_key
    key["allowedrole"]=[{"role":"admin"},{"role":"member"}]
    payload = json.dumps(key)
    
    headers = {"content-type": "application/json"}
    response = requests.post("http://127.0.0.1:818/api/sparts/ledger/auth", 
                    data=json.dumps(key), headers=headers)
    output = response.content.decode("utf-8").strip()
    statusinfo = json.loads(output)
    
    if statusinfo.get("status") and statusinfo.get("message"):
            
        status = statusinfo["status"]
        message = statusinfo["message"]
            
        if status == "success" and message == "authorized":
            
            b_url = config.get("DEFAULT", "url")
            client = CategoryBatch(base_url=b_url)
            response = client.update_category(category_id, category_name, 
                            description, private_key, public_key)
            print_msg(response)
            
        else:
            print(output)
    else:
        print(output)
        
################################################################################
#                                   PRINT                                      #
################################################################################
def amend_category_fields(inputstr):
    output = inputstr.replace("\\","")
    return output

def load_config():
    
    config = configparser.ConfigParser()
    config.set("DEFAULT", "url", "http://127.0.0.1:8008")
    return config

def print_msg(response):
    if response == None:
        print(ret_msg("failed","Exception raised","EmptyRecord","{}"))
    elif "batch_statuses?id" in response:
        print(ret_msg("success","OK","EmptyRecord","{}"))
    else:
        print(ret_msg("failed","Exception raised","EmptyRecord","{}"))
################################################################################
#                                   MAIN                                       #
################################################################################        
def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    if args.verbose is None:
        verbose_level = 0
    else:
        verbose_level = args.verbose

    setup_loggers(verbose_level=verbose_level)

    config = load_config()

    if args.command == "create":
        do_create_category(args, config)
    elif args.command == "list-category":
        do_list_category(args, config)
    elif args.command == "retrieve":
        do_retrieve_category(args, config)
    elif args.command == "update":
        do_update_category(args, config)
    else:
        raise CategoryException("invalid command: {}".format(args.command))

def ret_msg(status, message, result_type, result):
    msgJSON = "{}"
    key = json.loads(msgJSON)
    key["status"] = status
    key["message"] = message
    key["result_type"] = result_type
    key["result"] = json.loads(result)
   
    msgJSON = json.dumps(key)
    return msgJSON

def main_wrapper():
    try:
        main()
    except CategoryException as err:
        errmsg = str(err)
        if "404" in errmsg:
            exp = ret_msg("failed","404 Not Found","EmptyRecord","{}")
            print(CategoryException(exp))
           
        else:
            exp = ret_msg("failed",errmsg,"EmptyRecord","{}")
            print(CategoryException()) 
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
################################################################################
#                                                                              #
################################################################################
