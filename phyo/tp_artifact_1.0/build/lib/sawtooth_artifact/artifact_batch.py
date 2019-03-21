# Copyright 2016 Intel Corporation
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
from sawtooth_artifact.exceptions import ArtifactException
################################################################################
#                            GLOBAL FUNCTIONS                                  #
################################################################################
def _sha512(data):
    return hashlib.sha512(data).hexdigest()
################################################################################
#                                  CLASS                                       #
################################################################################
class ArtifactBatch:
    
    def __init__(self, base_url):
        self._base_url = base_url
################################################################################
#                            PUBLIC FUNCTIONS                                  #
################################################################################
    def create(self, private_key, public_key, artifact_id, artifact_alias, 
                artifact_name, artifact_type, artifact_checksum, artifact_label, 
                artifact_openchain):
        cur = self._get_block_num() 
        return self.artifact_transaction(private_key, public_key, artifact_id, 
                    artifact_alias, artifact_name, artifact_type, 
                    artifact_checksum, artifact_label, artifact_openchain, 
                    "0", cur, str(datetime.datetime.utcnow()), "create", "", "")
    
    def amend(self, private_key, public_key, artifact_id, artifact_alias, 
                artifact_name, artifact_type, artifact_checksum, artifact_label, 
                artifact_openchain):
        response_bytes = self.retrieve_artifact(artifact_id)
        
        if response_bytes != None:
            
            jresponse = json.loads(response_bytes.decode())
            
            if (jresponse["artifact_alias"] == artifact_alias and
                jresponse["artifact_name"] == artifact_name and
                jresponse["artifact_type"] == artifact_type and
                jresponse["artifact_checksum"] == artifact_checksum and
                jresponse["artifact_label"] == artifact_label and
                jresponse["artifact_openchain"] == artifact_openchain) :
                return None
            else:
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, artifact_alias, artifact_name,
                            artifact_type, artifact_checksum, artifact_label,
                            artifact_openchain, jresponse["cur_block"], cur, 
                            str(datetime.datetime.utcnow()), "amend", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                            
        return None
        
    def list_artifact(self):
        artifact_prefix = self._get_prefix()

        result = self._send_request(
            "state?address={}".format(artifact_prefix)
        )

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                base64.b64decode(entry["data"]) for entry in encoded_entries
            ]

        except BaseException:
            return None
    
    def retrieve_artifact(self, artifact_id, all_flag=False, range_flag=None):
        if all_flag:
            
            retVal = []
            
            response = self.retrieve_artifact(artifact_id).decode()
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
            address = self._get_address(artifact_id)
    
            result = self._send_request("state/{}".format(address), 
                        artifact_id=artifact_id)
            try:
                return base64.b64decode(yaml.safe_load(result)["data"])
    
            except BaseException:
                return None
    
    def add_artifact(self, private_key, public_key, artifact_id, 
                sub_artifact_id, path, deleteSub=False):
        if deleteSub:
            response_bytes = self.retrieve_artifact(artifact_id)
            
            if response_bytes != None:
                
                jresponse = json.loads(response_bytes.decode())
                
                if len(jresponse["artifact_list"]) == 0:
                    raise ArtifactException("No {} to remove from this {}." \
                                .format("Sub-Artifact", "Artifact")
                        )
                        
                art_dict = {
                    "artifact_id"   : sub_artifact_id,
                    "artifact_path" : path
                }
                
                if art_dict not in jresponse["artifact_list"]:
                    raise ArtifactException("No such {} in this {}." \
                                .format("Sub-Artifact", "Artifact")
                        )
                        
                jresponse["artifact_list"].remove(art_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["artifact_alias"],
                            jresponse["artifact_name"],
                            jresponse["artifact_type"],
                            jresponse["artifact_checksum"],
                            jresponse["artifact_label"],
                            jresponse["artifact_openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddArtifact", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
        else:
            response_bytes = self.retrieve_artifact(artifact_id)
            
            self._validate_sub_artifact_id(sub_artifact_id)
            
            if response_bytes != None:
                
                jresponse = json.loads(response_bytes.decode())
                
                art_dict = {
                    "artifact_id"   : sub_artifact_id,
                    "artifact_path" : path
                }
                
                if len(jresponse["artifact_list"]) != 0:
                    
                    # no dup art_id allowed in art_list
                    # for eachDictionary in jresponse["artifact_list"]:
                    #     if eachDictionary["artifact_id"] == sub_artifact_id:
                    #         raise ArtifactException(
                    #                 "{} already exists for this {}.".format(
                    #                         "Sub-Artifact", "Artifact"
                    #                     )
                    #             )
                    
                    # no dup art_dict allowed in art_list
                    if art_dict in jresponse["artifact_list"]:
                        raise ArtifactException(
                                "{} already exists for this {}.".format(
                                        "Artifact-Dictionary", "Artifact"
                                    )
                            )        
                jresponse["artifact_list"].append(art_dict)
                    
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["artifact_alias"],
                            jresponse["artifact_name"],
                            jresponse["artifact_type"],
                            jresponse["artifact_checksum"],
                            jresponse["artifact_label"],
                            jresponse["artifact_openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddArtifact", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
    
    def add_uri(self, private_key, public_key, artifact_id, version, checksum, 
                content_type, size, uri_type, location, deleteURI=False):
        if deleteURI:
            response_bytes = self.retrieve_artifact(artifact_id)
            
            if response_bytes != None:
                
                jresponse = json.loads(response_bytes.decode())
                
                if len(jresponse["uri_list"]) == 0:
                    raise ArtifactException("No {} to remove from this {}." \
                                .format("URI", "Artifact")
                        )
                
                uri_dict = {
                    "uri_version"       : version,
                    "uri_content_type"  : content_type,
                    "uri_size"          : size,
                    "uri_type"          : uri_type,
                    "uri_location"      : location
                }
                
                if uri_dict not in jresponse["uri_list"]:
                    raise ArtifactException("No such {} in this {}." \
                                .format("URI", "Artifact")
                        )
                        
                jresponse["uri_list"].remove(uri_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["artifact_alias"],
                            jresponse["artifact_name"],
                            jresponse["artifact_type"],
                            jresponse["artifact_checksum"],
                            jresponse["artifact_label"],
                            jresponse["artifact_openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddArtifact", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
        else:
            response_bytes = self.retrieve_artifact(artifact_id)
            
            # self._validate_URI() # how???
            
            if response_bytes != None:
                
                jresponse = json.loads(response_bytes.decode())
                
                uri_dict = {
                    "uri_version"       : version,
                    "uri_content_type"  : content_type,
                    "uri_size"          : size,
                    "uri_type"          : uri_type,
                    "uri_location"      : location
                }
                
                if len(jresponse["uri_list"]) != 0:
                    if uri_dict in jresponse["uri_list"]:
                        raise ArtifactException(
                                "{} already exists for this {}.".format(
                                        "URI-Dictionary", "Artifact"
                                    )
                            )
                jresponse["uri_list"].append(uri_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["artifact_alias"],
                            jresponse["artifact_name"],
                            jresponse["artifact_type"],
                            jresponse["artifact_checksum"],
                            jresponse["artifact_label"],
                            jresponse["artifact_openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddURI", 
                            jresponse["artifact_list"], jresponse["uri_list"])
            
            return None
################################################################################
#                            PRIVATE FUNCTIONS                                 #
################################################################################   
    def _get_prefix(self):
        return _sha512('artifact'.encode('utf-8'))[0:6]

    def _get_address(self, artifact_id):
        artifact_prefix = self._get_prefix()
        address = _sha512(artifact_id.encode('utf-8'))[0:64]
        return artifact_prefix + address
    
    def _get_block_num(self):
        artifact_prefix = self._get_prefix()
        
        result = self._send_request(
            "blocks?={}".format(artifact_prefix)
        )
        
        if result != None or result != "":
            result = json.loads(result)
            return str(len(result["data"]))
        return None
    
    def _get_payload_(self, blocknum):
        artifact_prefix = self._get_prefix()
        
        result = self._send_request(
            "blocks?={}".format(artifact_prefix)
        )
        
        if result != None or result != "":
            result = json.loads(result)
            payload = result["data"][-(blocknum + 1)]["batches"][0]\
                        ["transactions"][0]["payload"]
            
            return base64.b64decode(payload)
        return None
    
    def _validate_sub_artifact_id(self, sub_artifact_id):
        artifact_prefix = _sha512('artifact'.encode('utf-8'))[0:6]
        address = _sha512(sub_artifact_id.encode('utf-8'))[0:64]
        address = artifact_prefix + address
        self._send_request("state/{}".format(address))
    
    def _send_request(
            self, suffix, data=None,
            content_type=None, artifact_id=None):
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
                raise ArtifactException(
                        "No such artifact as {}".format(artifact_id)
                    )

            elif not result.ok:
                raise ArtifactException("Error {} {}".format(
                    result.status_code, result.reason))

        except BaseException as err:
            raise ArtifactException(err)
            
        return result.text

    def artifact_transaction(self, private_key, public_key, artifact_id, 
                artifact_alias, artifact_name, artifact_type, 
                artifact_checksum, artifact_label, artifact_openchain, 
                prev, cur, timestamp, action, artifact_list, uri_list):
        
        self._public_key = public_key
        self._private_key = private_key
        
        payload = {
            "artifact_id"           : str(artifact_id),
            "artifact_alias"        : str(artifact_alias),
            "artifact_name"         : str(artifact_name),
            "artifact_type"         : str(artifact_type),
            "artifact_checksum"     : str(artifact_checksum),
            "artifact_label"        : str(artifact_label),
            "artifact_openchain"    : str(artifact_openchain),
            "action"                : str(action),
            "prev_block"            : str(prev),
            "cur_block"             : str(cur),
            "timestamp"             : str(timestamp),
            "artifact_list"         : artifact_list,
            "uri_list"              : uri_list
        }
        payload = json.dumps(payload).encode()
        
        address = self._get_address(artifact_id)

        header = TransactionHeader(
            signer_public_key = self._public_key,
            family_name = "artifact",
            family_version = "1.0",
            inputs = [address],
            outputs = [address],
            dependencies = [],
            # payload_encoding="csv-utf8",
            payload_sha512 = _sha512(payload),
            batcher_public_key = self._public_key,
            nonce = time.time().hex().encode()
        ).SerializeToString()

        # signature = signing.sign(header, self._private_key)
        signature = CryptoFactory(create_context('secp256k1')) \
            .new_signer(Secp256k1PrivateKey.from_hex(self._private_key)).sign(header)

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
            signer_public_key = self._public_key,
            transaction_ids = transaction_signatures
        ).SerializeToString()

        # signature = signing.sign(header, self._private_key)
        signature = CryptoFactory(create_context('secp256k1')) \
            .new_signer(Secp256k1PrivateKey.from_hex(self._private_key)) \
            .sign(header)

        batch = Batch(
            header = header,
            transactions = transactions,
            header_signature = signature
        )
        return BatchList(batches=[batch])
################################################################################
#                                                                              #
################################################################################
