# Copyright 2016 Intel Corporation
# Copyright 2017 Wind River

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
import hashlib
import base64
from base64 import b64encode
import time
import requests
import yaml
import datetime
import json

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from sawtooth_part.exceptions import PartException
################################################################################
#                            GLOBAL FUNCTIONS                                  #
################################################################################
def _sha512(data):
    return hashlib.sha512(data).hexdigest()
################################################################################
#                                  CLASS                                       #
################################################################################
class PartBatch:
    
    def __init__(self, base_url):
        self._base_url = base_url
################################################################################
#                            PUBLIC FUNCTIONS                                  #
################################################################################    
    def create(self, pt_id, pt_name, checksum, version, alias, licensing, label,
                description, private_key, public_key):
        cur = self._get_block_num()
        return self.create_part_transaction(pt_id, pt_name, checksum, version, 
                    alias, licensing, label, description, "create", private_key,
                    public_key, [], [], [], "0", cur, 
                    str(datetime.datetime.utcnow()))
  
    def amend(self, pt_id, pt_name, checksum, version, alias, licensing, label,
                description, private_key, public_key):
        response_bytes = self.retrieve_part(pt_id)
        
        if response_bytes != None:
            response = str(response_bytes)
            response = response[response.find("{") : response.find("}") + 1]
            
            jresponse = json.loads(response)
            
            if (jresponse["pt_name"]        == pt_name      and
                jresponse["pt_checksum"]    == checksum     and
                jresponse["pt_version"]     == version      and
                jresponse["pt_alias"]       == alias        and
                jresponse["pt_licensing"]   == licensing    and
                jresponse["pt_label"]       == label        and
                jresponse["description"]    == description):
                return None
            else:
                cur = self._get_block_num()
                return self.create_part_transaction(pt_id, pt_name, checksum, 
                            version, alias, licensing, label, description, 
                            "amend", private_key, public_key, 
                            jresponse["artifact_id"], 
                            jresponse["category_id"],
                            jresponse["supplier_id"], 
                            jresponse["cur_block"], cur, 
                            str(datetime.datetime.utcnow()))
        
        return None
    
    def add_artifact(self, pt_id, artifact_id, private_key, public_key):
        response_bytes = self.retrieve_part(pt_id)
        
        self._validate_artifact_id(artifact_id)
        
        if response_bytes != None:
            response = str(response_bytes)
            response = response[response.find("{") : response.find("}") + 1]
            
            jresponse = json.loads(response)
            
            if artifact_id not in jresponse["artifact_id"]:
                jresponse["artifact_id"].append(artifact_id)
            else:
                raise PartException(
                        "Artifact already exists for this Part."
                    )
            
            cur = self._get_block_num()
            return self.create_part_transaction(pt_id, jresponse["pt_name"], 
                        jresponse["pt_checksum"], jresponse["pt_version"], 
                        jresponse["pt_alias"], jresponse["pt_licensing"], 
                        jresponse["pt_label"], jresponse["description"], 
                        "AddArtifact", private_key, public_key, 
                        jresponse["artifact_id"], jresponse["category_id"], 
                        jresponse["supplier_id"], jresponse["cur_block"], cur, 
                        str(datetime.datetime.utcnow()))
        return None
        
    def add_category(self, pt_id, category_id, private_key, public_key):
        response_bytes = self.retrieve_part(pt_id)
        
        self._validate_category_id(category_id)
        
        if response_bytes != None:
            response = str(response_bytes)
            response = response[response.find("{") : response.find("}") + 1]
            
            jresponse = json.loads(response)
            
            if category_id not in jresponse["category_id"]:
                jresponse["category_id"].append(category_id)
            else:
                raise PartException(
                        "Category already exists for this Part."
                    )
            
            cur = self._get_block_num()
            return self.create_part_transaction(pt_id, jresponse["pt_name"], 
                        jresponse["pt_checksum"], jresponse["pt_version"], 
                        jresponse["pt_alias"], jresponse["pt_licensing"], 
                        jresponse["pt_label"], jresponse["description"], 
                        "AddCategory", private_key, public_key, 
                        jresponse["artifact_id"], jresponse["category_id"], 
                        jresponse["supplier_id"], jresponse["cur_block"], cur, 
                        str(datetime.datetime.utcnow()))
        return None
   
    def add_supplier(self, pt_id, supplier_id, private_key, public_key):
        response_bytes = self.retrieve_part(pt_id)
        
        self._validate_supplier_id(supplier_id)
        
        if response_bytes != None:
            response = str(response_bytes)
            response = response[response.find("{") : response.find("}") + 1]
            
            jresponse = json.loads(response)
            
            if supplier_id not in jresponse["supplier_id"]:
                jresponse["supplier_id"].append(supplier_id)
            else:
                raise PartException(
                        "Category already exists for this Part."
                    )
            
            cur = self._get_block_num()
            return self.create_part_transaction(pt_id, jresponse["pt_name"], 
                        jresponse["pt_checksum"], jresponse["pt_version"], 
                        jresponse["pt_alias"], jresponse["pt_licensing"], 
                        jresponse["pt_label"], jresponse["description"], 
                        "AddSupplier", private_key, public_key, 
                        jresponse["artifact_id"], jresponse["category_id"], 
                        jresponse["supplier_id"], jresponse["cur_block"], cur, 
                        str(datetime.datetime.utcnow()))
        return None

    def list_part(self):
        part_prefix = self._get_prefix()

        result = self._send_request(
            "state?address={}".format(part_prefix)
        )

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                base64.b64decode(entry["data"]) for entry in encoded_entries
            ]

        except BaseException:
            return None
    
    def retrieve_part(self, pt_id, all_flag=False, range_flag=None):
        if all_flag:
            
            retVal = []
            response = self.retrieve_part(pt_id).decode()
            
            response = response[response.find("{"):]
            response = json.loads(response)
            
            if range_flag != None:
                curTime = int(response["timestamp"].split()[0].replace("-", ""))
                if (curTime <= int(range_flag[1]) and 
                        curTime >= int(range_flag[0])):
                    jresponse = json.dumps(response)
                    retVal.append(jresponse)
            else:
                jresponse = json.dumps(response)
                retVal.append(jresponse)
            
            while str(response["prev_block"]) != "0":
                
                response = json.loads(self._get_payload_(
                                int(response["prev_block"])).decode())
                
                timestamp       = response["timestamp"] 
                
                del response["action"]
                
                jresponse = json.dumps(response)
                
                if range_flag != None:
                    curTime = int(timestamp.split()[0].replace("-", ""))
                    if curTime < int(range_flag[0]):
                        break
                    elif curTime <= int(range_flag[1]):
                        retVal.append(jresponse)
                else:
                    retVal.append(jresponse)
                
            retVal = str(retVal).replace("'", '')
            
            return json.dumps(retVal)
        else:
            address = self._get_address(pt_id)
    
            result = self._send_request("state/{}".format(address), pt_id=pt_id
                                        )
            try:
                return base64.b64decode(yaml.safe_load(result)["data"])
    
            except BaseException:
                return None
################################################################################
#                            PRIVATE FUNCTIONS                                 #
################################################################################
    def _get_prefix(self):
        return _sha512('pt'.encode('utf-8'))[0:6]
    
    def _get_address(self, pt_id):
        part_prefix = self._get_prefix()
        address = _sha512(pt_id.encode('utf-8'))[0:64]
        return part_prefix + address
    
    def _get_block_num(self):
        part_prefix = self._get_prefix()

        result = self._send_request(
            "blocks?={}".format(part_prefix)
        )
        
        if result != None or result != "":
            result = json.loads(result)
            return str(len(result["data"]))
        return None
    
    def _get_payload_(self, blocknum):
        part_prefix = self._get_prefix()

        result = self._send_request(
            "blocks?={}".format(part_prefix)
        )
        
        if result != None or result != "":
            result = json.loads(result)
            payload = result["data"][-(blocknum + 1)]["batches"][0]\
                        ["transactions"][0]["payload"]
            
            return base64.b64decode(payload)
        return None
    
    def _validate_artifact_id(self, artifact_id):
        artifact_prefix = _sha512('artifact'.encode('utf-8'))[0:6]
        address = _sha512(artifact_id.encode('utf-8'))[0:64]
        address = artifact_prefix + address
        self._send_request("state/{}".format(address))
    
    def _validate_category_id(self, category_id):
        category_prefix = _sha512("category".encode("utf-8"))[0:6]
        address = _sha512(category_id.encode("utf-8"))[0:64]
        address = category_prefix + address
        self._send_request("state/{}".format(address))
    
    def _validate_supplier_id(self, supplier_id):
        category_prefix = _sha512("supplier".encode("utf-8"))[0:6]
        address = _sha512(supplier_id.encode("utf-8"))[0:64]
        address = category_prefix + address
        self._send_request("state/{}".format(address))
    
    def _send_request(
            self, suffix, data=None,
            content_type=None, pt_id=None):
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {}
        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise PartException("No part found: {}".format(pt_id))

            elif not result.ok:
                raise PartException("Error {}: {}".format(
                    result.status_code, result.reason))

        except BaseException as err:
            raise PartException(err)

        return result.text
   
    def create_part_transaction(self, pt_id, pt_name, checksum, version, alias, 
                            licensing, label, description, action, private_key, 
                            public_key, artifact_id, category_id, supplier_id,
                            prev, cur, timestamp):
        
        self._public_key = public_key
        self._private_key = private_key
        
        payload = {
            "pt_id"         : str(pt_id),
            "pt_name"       : str(pt_name),
            "pt_checksum"   : str(checksum),
            "pt_version"    : str(version),
            "pt_alias"      : str(alias),
            "pt_licensing"  : str(licensing),
            "pt_label"      : str(label),
            "description"   : str(description),
            "action"        : str(action),
            "prev_block"    : str(prev),
            "cur_block"     : str(cur),
            "timestamp"     : str(timestamp),
            "artifact_id"   : artifact_id,
            "category_id"   : category_id,
            "supplier_id"   : supplier_id
        }
        payload = json.dumps(payload).encode()
        
        # Construct the address
        address = self._get_address(pt_id)

        header = TransactionHeader(
            signer_public_key = self._public_key,
            family_name = "pt",
            family_version = "1.0",
            inputs = [address],
            outputs = [address],
            dependencies = [],
            payload_sha512 = _sha512(payload),
            batcher_public_key = self._public_key,
            nonce = time.time().hex().encode()
        ).SerializeToString()
        
        signature = CryptoFactory(create_context('secp256k1')) \
            .new_signer(Secp256k1PrivateKey.from_hex(self._private_key)) \
            .sign(header)

        transaction = Transaction(
            header = header,
            payload = payload,
            header_signature = signature
        )

        batch_list = self._create_batch_list([transaction])
        
        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream'
        )

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = CryptoFactory(create_context('secp256k1')) \
            .new_signer(Secp256k1PrivateKey.from_hex(self._private_key)) \
            .sign(header)


        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature
        )
        return BatchList(batches=[batch])
################################################################################
#                                                                              #
################################################################################
