# Copyright 2016 Intel Corporation
# Copyright 2019 Wind River Systems
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
################################################################################
#                         LIBRARIES & DEPENDENCIES                             #
################################################################################
import hashlib
import base64
import time
import requests
import yaml
import datetime
import json
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
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
    """
    Creates the string of sha512 hashed to the passed in data.
    
    Args:
        data (bytes): The data to be hashed
    
    Returns:
        type: str
        The sha512 hashed data in string of hex values.
        
    """
    return hashlib.sha512(data).hexdigest()
################################################################################
#                                  CLASS                                       #
################################################################################
class ArtifactBatch:
    """
    Class for creating batch of the Transaction Family : Artifact
    
    Attributes:
        base_url (str): The base url of the transaction family
    
    """
    
    def __init__(self, base_url):
        """
        Constructs the ArtifactBatch object.
        
        Args:
            base_url (str): The base url of the transaction family
        
        """
        self._base_url = base_url
################################################################################
#                            PUBLIC FUNCTIONS                                  #
################################################################################
    def create_artifact(self, private_key, public_key, artifact_id,
            artifact_alias, artifact_name, artifact_type, artifact_checksum,
            artifact_label, artifact_openchain):
        """
        Constructs the batch payload for the "create" command.
        
        Args:
            artifact_id (str): The uuid of the artifact
            artifact_alias (str): The alias of the artifact
            artifact_name (str): The name of the artifact
            artifact_type (str): The type of the artifact
            artifact_checksum (str): The checksum of the artifact
            artifact_label (str): The label of the artifact
            artifact_openchain (str): The openchain of the artifact
            private_key (str): The private key of the user
            public_key (str): The public key of the user
        
        Returns:
            type: Batch
            The batch object which pertains all the data associating with the 
            "create" command.
                
                or
            
            type: None
            None object if the UUID already exists in the ledger.
            
        """
        # Checking if the uuid is unique
        address = self._get_address(artifact_id)
        response_bytes = self._send_request("state/{}".format(address),
                        artifact_id=artifact_id, creation=True
                    )
        if response_bytes != None:
            return None
        
        # Creating the batch object to be returned
        cur = self._get_block_num() 
        return self.artifact_transaction(private_key, public_key, artifact_id, 
                    artifact_alias, artifact_name, artifact_type, 
                    artifact_checksum, artifact_label, artifact_openchain, 
                    "0", cur, str(datetime.datetime.utcnow()), "create", "", "")
    
    def amend_artifact(self, private_key, public_key, artifact_id,
            artifact_alias, artifact_name, artifact_type, artifact_checksum,
            artifact_label, artifact_openchain):
        """
        Constructs the batch payload for the "amend" command.
        
        Args:
            artifact_id (str): The uuid of the artifact
            artifact_alias (str): The alias of the artifact
            artifact_name (str): The name of the artifact
            artifact_type (str): The type of the artifact
            artifact_checksum (str): The checksum of the artifact
            artifact_label (str): The label of the artifact
            artifact_openchain (str): The openchain of the artifact
            private_key (str): The private key of the user
            public_key (str): The public key of the user
        
        Returns:
            type: Batch
            The batch object which pertains all the data associating with the
            "amend" command.
            
                or
            
            type: None
            None object if the UUID does not exist in the ledger.
            
                or 
            
            type: list pertaining None
            List containing only None object if no member was amended.
            
        """
        # Checking if the uuid exists
        response_bytes = self.retrieve_artifact(artifact_id)
        if response_bytes != None:
            
            # Loading the data to perform checks
            jresponse = json.loads(response_bytes.decode())
            
            # Checking if params are "null"; if yes, replace with prior values
            if artifact_alias == "null":
                artifact_alias = jresponse["alias"]
            if artifact_name == "null":
                artifact_name = jresponse["name"]
            if artifact_type == "null":
                artifact_type = jresponse["content_type"]
            if artifact_checksum == "null":
                artifact_checksum = jresponse["checksum"]
            if artifact_label == "null":
                artifact_label = jresponse["label"]
            if artifact_openchain == "null":
                artifact_openchain = jresponse["openchain"]
            
            # Checking if any of the params were changed; if not, return [None]
            if (jresponse["alias"] == artifact_alias and
                jresponse["name"] == artifact_name and
                jresponse["content_type"] == artifact_type and
                jresponse["checksum"] == artifact_checksum and
                jresponse["label"] == artifact_label and
                jresponse["openchain"] == artifact_openchain) :
                return [None]
            else:
                # Creating the batch object to be returned
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, artifact_alias, artifact_name,
                            artifact_type, artifact_checksum, artifact_label,
                            artifact_openchain, jresponse["cur_block"], cur, 
                            str(datetime.datetime.utcnow()), "amend", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                            
        return None
        
    def list_artifact(self):
        """
        Fetches the data from ledger and constructs the list of artifact.
        
        Returns:
            type: list of dict
            List of JSON (Python dict) associated with 
            the Transaction Family : Artifact.
            
                or
            
            type: None
            None object if deserialization of the data failed.
        
        """
        artifact_prefix = self._get_prefix()

        result = self._send_request(
            "state?address={}".format(artifact_prefix)
        )

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                json.loads(base64.b64decode(entry["data"]).decode()) for entry \
                    in encoded_entries
            ]

        except BaseException:
            return None
    
    def retrieve_artifact(self, artifact_id, all_flag=False, range_flag=None):
        """
        Fetches the data associating with UUID from ledger.
        
        Args:
            artifact_id (str): The uuid of the artifact
            all_flag (bool): The flag for "--all" option (default False)
            range_flag (list of int):
                The flag for "--range" option (default None)
            
        Returns:
            type: bytes
            Bytes containing the data associated to the UUID.
            
                or
            
            type: list of dict
            List of JSON (Python dict) associated with the UUID.
                * If "--all" or "--range" are not default values
            
                or
            
            type: None
            None object if decoding failed.
        
        """
        # Checking if "--all" is invoked
        if all_flag:
            
            # Loading and instatiating to perform checks
            retVal = []
            
            response = self.retrieve_artifact(artifact_id).decode()
            response = json.loads(response)
            
            # Checking if "--range" is invoked and performing checks to append
            if range_flag != None:
                curTime = int(response["timestamp"].split()[0].replace("-", ""))
                if (curTime <= int(range_flag[1]) and 
                        curTime >= int(range_flag[0])):
                    retVal.append(response)
            else:
                retVal.append(response)
            
            # While not "create" perform checks to append to list    
            while str(response["prev_block"]) != "0":
                
                response = json.loads(self._get_payload_(
                                int(response["prev_block"])).decode())
                
                timestamp       = response["timestamp"] 
                
                del response["action"]
                
                if range_flag != None:
                    curTime = int(timestamp.split()[0].replace("-", ""))
                    if curTime < int(range_flag[0]):
                        break
                    elif curTime <= int(range_flag[1]):
                        retVal.append(response)
                else:
                    retVal.append(response)
            
            # Returning the list of JSON
            return retVal
        else:
            address = self._get_address(artifact_id)
    
            result = self._send_request("state/{}".format(address), 
                        artifact_id=artifact_id)
            try:
                return base64.b64decode(yaml.safe_load(result)["data"])
    
            except BaseException:
                return None
    
    def add_artifact(self, private_key, public_key, artifact_id, 
                sub_artifact_id, path, del_flag=False):
        """
        Constructs the batch payload for the "AddArtifact" command.
        
        Args:
            artifact_id (str): The uuid of the artifact
            sub_artifact_id (str): the uuid of the sub-artifact
            private_key (str): The private key of the user
            public_key (str): The public key of the user
            del_flag (bool): The flag for "--delete" option (default False)
        
        Returns:
            type: Batch
            The batch object which pertains all the data associating with the
            "AddArtifact" command.
            
                or
            
            type: None
            None object if UUID does not exist in the ledger.
            
                or
            
            type: list pertaining None and str
            List containing None object and error message:
                * If "--delete"
                    > If "artifact_list" is empty
                    > If "art_dict" is not in "artifact_list"
                * If "art_dict" is in "artifact_list"
            
        """
        # Checking if "--delete" is invoked
        if del_flag:
            
            # Loading the data to perform checks
            response_bytes = self.retrieve_artifact(artifact_id)
            
            # Checking if uuid exists
            if response_bytes != None:
                
                # Loading the state of uuid to perform checks
                jresponse = json.loads(response_bytes.decode())
                
                if len(jresponse["artifact_list"]) == 0:
                    return  [
                                None,
                                "No {} to remove from this {}." \
                                    .format("Sub-Artifact", "Artifact")
                            ]
                        
                art_dict = {
                    "uuid" : sub_artifact_id,
                    "path" : path
                }
                
                if art_dict not in jresponse["artifact_list"]:
                    return  [
                                None, 
                                "No such {} in this {}." \
                                    .format("Sub-Artifact", "Artifact")
                            ]
                
                # Removing the "art_dict" from "artifact_list"
                # and creating the batch object to be returned        
                jresponse["artifact_list"].remove(art_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["alias"],
                            jresponse["name"],
                            jresponse["content_type"],
                            jresponse["checksum"],
                            jresponse["label"],
                            jresponse["openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddArtifact", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
        else:
            # Loading the data to perform checks
            response_bytes = self.retrieve_artifact(artifact_id)
            
            # Checking if uuid exists
            if response_bytes != None:
                
                # Checking if sub-artifact to be added exists
                if self._validate_sub_artifact_id(sub_artifact_id) == None:
                    return  [
                                None,
                                "ArtifactException : UUID does not exist."
                            ]
                
                # Loading the state of uuid to perform checks
                jresponse = json.loads(response_bytes.decode())
                
                art_dict = {
                    "uuid" : sub_artifact_id,
                    "path" : path
                }
                
                if len(jresponse["artifact_list"]) != 0:
                    
                    # no dup art_dict allowed in art_list
                    if art_dict in jresponse["artifact_list"]:
                        return  [
                                    None,
                                    "{} already exists for this {}.".format(
                                        "Artifact-Dictionary", "Artifact"
                                    )
                                ]
                
                # Creating a batch object to be returned along with 
                # updated "artifact_list"                    
                jresponse["artifact_list"].append(art_dict)
                    
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["alias"],
                            jresponse["name"],
                            jresponse["content_type"],
                            jresponse["checksum"],
                            jresponse["label"],
                            jresponse["openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddArtifact", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
    
    def add_uri(self, private_key, public_key, artifact_id, version, checksum, 
                content_type, size, uri_type, location, del_flag=False):
        """
        Constructs the batch payload for the "AddURI" command.
        
        Args:
            artifact_id (str): The uuid of the artifact
            version (str): The version of the uri
            checksum (str): The checksum of the uri
            content_type (str): The content-type of the uri
            size (str): The size of the uri
            url_type (str): The url-type of the uri
            location (str): The location of the uri
            private_key (str): The private key of the user
            public_key (str): The public key of the user
            del_flag (bool): The flag for "--delete" option (default False)
        
        Returns:
            type: Batch
            The batch object which pertains all the data associating with the
            "AddURI" command.
            
                or
            
            type: None
            None object if UUID does not exist in the ledger.
            
                or
            
            type: list pertaining None and str
            List containing None object and error message:
                * If "--delete"
                    > If "uri_list" is empty
                    > If "uri_dict" is not in "uri_list"
                * If "uri_dict" is in "uri_list"
            
        """
        # Checking if "--delete" is invoked
        if del_flag:
            
            # Loading the data to perform checks
            response_bytes = self.retrieve_artifact(artifact_id)
            
            # Checking if uuid exists
            if response_bytes != None:
                
                # Loading the state of uuid to perform checks
                jresponse = json.loads(response_bytes.decode())
                
                if len(jresponse["uri_list"]) == 0:
                    return  [
                                None, 
                                "No {} to remove from this {}." \
                                    .format("URI", "Artifact")
                            ]
                
                uri_dict = {
                    "version"       : version,
                    "checksum"      : checksum,
                    "content_type"  : content_type,
                    "size"          : size,
                    "uri_type"      : uri_type,
                    "location"      : location
                }
                
                if uri_dict not in jresponse["uri_list"]:
                    return  [
                                None,
                                "No such {} in this {}." \
                                    .format("URI", "Artifact")
                            ]
                
                # Removing the "uri_dict" from "uri_list"
                # and creating the batch object to be returned        
                jresponse["uri_list"].remove(uri_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["alias"],
                            jresponse["name"],
                            jresponse["content_type"],
                            jresponse["checksum"],
                            jresponse["label"],
                            jresponse["openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddURI", 
                            jresponse["artifact_list"], jresponse["uri_list"])
                
            return None
        else:
            # Loading the data to perform checks
            response_bytes = self.retrieve_artifact(artifact_id)
            
            # Checking if uuid exists
            if response_bytes != None:
                
                # Loading the state of uuid to perform checks
                jresponse = json.loads(response_bytes.decode())
                
                uri_dict = {
                    "version"       : version,
                    "checksum"      : checksum,
                    "content_type"  : content_type,
                    "size"          : size,
                    "uri_type"      : uri_type,
                    "location"      : location
                }
                
                if len(jresponse["uri_list"]) != 0:
                    if uri_dict in jresponse["uri_list"]:
                        return  [
                                    None, 
                                    "{} already exists for this {}.".format(
                                            "URI-Dictionary", "Artifact"
                                        )
                                ]
                
                # Creating a batch object to be returned along with 
                # updated "uri_list"                
                jresponse["uri_list"].append(uri_dict)
                
                cur = self._get_block_num()
                return self.artifact_transaction(private_key, public_key,
                            artifact_id, jresponse["alias"],
                            jresponse["name"],
                            jresponse["content_type"],
                            jresponse["checksum"],
                            jresponse["label"],
                            jresponse["openchain"],
                            jresponse["cur_block"], cur,
                            str(datetime.datetime.utcnow()), "AddURI", 
                            jresponse["artifact_list"], jresponse["uri_list"])
            
            return None
################################################################################
#                            PRIVATE FUNCTIONS                                 #
################################################################################   
    def _get_prefix(self):
        """
        Constructs and returns a string of SHA512 hashed data of
        the Transaction Family : Artifact.
        
        Returns:
            type: str
            The first 6 characters of the SHA512 hashed data of
            the Transaction Family : Artifact.
            
        """
        return _sha512("artifact".encode("utf-8"))[0:6]

    def _get_address(self, artifact_id):
        """
        Constructs and returns a string of unique hashed data for the
        passed in UUID.
        
        Args:
            artifact_id (str): The uuid of the artifact
        
        Returns:
            type: str
            The address-to-be, which associates the uuid and the prefix.
            
        """
        artifact_prefix = self._get_prefix()
        address = _sha512(artifact_id.encode("utf-8"))[0:64]
        return artifact_prefix + address
    
    def _get_block_num(self):
        """
        Fetches the current block ID of the ledger.
        
        Returns:
            type: str
            The current block ID of the ledger as a string.
            
                or
            
            type: None
            None object if there is no block in the ledger.
        
        """
        artifact_prefix = self._get_prefix()
        
        result = self._send_request(
            "blocks?={}".format(artifact_prefix)
        )
        
        if result != None or result != "":
            result = json.loads(result)
            return str(len(result["data"]))
        return None
    
    def _get_payload_(self, blocknum):
        """
        Fetches the payload associated with the given block ID in the ledger.
        
        Args:
            blocknum (int): The block ID of the previous state of the UUID
        
        Returns:
            type: bytes
            The payload on the given block ID in bytes.
            
            type: None
            None object if there is no block in the ledger.
            
        """
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
        """
        Validates if the sub-artifact UUID exists in the ledger.
        
        Args:
            sub_artifact_id (str): The uuid of the sub-artifact
        
        Returns:
            type: str
            Data as string if UUID exist in the ledger.
            
                or
            
            type: None
            None object if UUID does not exist in the ledger.
            
        """
        artifact_prefix = _sha512("artifact".encode("utf-8"))[0:6]
        address = _sha512(sub_artifact_id.encode("utf-8"))[0:64]
        address = artifact_prefix + address
        return self._send_request("state/{}".format(address))
    
    def _send_request(
            self, suffix, data=None, content_type=None,
            artifact_id=None, creation=False):
        """
        Performs RESTful API call on the given params.
        
        Args:
            suffix (str): The suffix of the url in query
            data (str): The data to be sent in POST request (default None)
            content_type (str): The data type (default None)
            artifact_id (str): The uuid of the artifact (default None)
            creation (bool): The flag for "create" command (default False)
        
        Returns:
            type: str
            Data associated with suffix as a string.
            
                or
                
            type: None
            None object if any exception occurs or "404" was raised during
            "create" command.
            
        Raises:
            ArtifactException:
                * If "404" was raised for the request
                * If status was "sucessful"
            
        """
        # Building the URL
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {} 

        if content_type is not None:
            headers["Content-Type"] = content_type
        
        # Performing appropriate RESTful API
        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                if creation:
                    return None
                raise ArtifactException(
                        "No such artifact as {}".format(artifact_id)
                    )

            elif not result.ok:
                raise ArtifactException("Error {} {}".format(
                    result.status_code, result.reason))

        except BaseException as err:
            print(err)
            return None
        
        # Returning the data as string   
        return result.text

    def artifact_transaction(self, private_key, public_key, artifact_id, 
                artifact_alias, artifact_name, artifact_type, 
                artifact_checksum, artifact_label, artifact_openchain, 
                prev, cur, timestamp, action, artifact_list, uri_list):
        """
        Constructs the Batch to be posted and sent the request to be posted on
        the ledger.
        
        Args:
            private_key (str): The private key of the user
            public_key (str): The public key of the user
            artifact_id (str): The uuid of the artifact
            artifact_alias (str): The alias of the artifact
            artifact_name (str): The name of the artifact
            artifact_type (str): The type of the artifact
            artifact_checksum (str): The checksum of the artifact
            artifact_label (str): The label of the artifact
            artifact_openchain (str): The openchain of the artifact
            artifact_list (list of dict):
                The list of the sub-artifact dictionary associated with
                the artifact
            uri_list (list of dict):
                The list of the uri dictionary associated with the artifact
            prev (str): The previous block id of the transaction (default "0")
            cur (str): the current block id of the transaction
            timestamp (str): The UTC time for when the transaction was submitted
            action (str): The action performed
            
        Returns:
            type: str
            Data associated with suffix as a string.
            
                or
            
            type: None
            None object if _send_request failed.
            
        """
        # Constructing Batch to be sent and stored
        self._public_key = public_key
        self._private_key = private_key
        
        payload = {
            "uuid"          : str(artifact_id),
            "alias"         : str(artifact_alias),
            "name"          : str(artifact_name),
            "content_type"  : str(artifact_type),
            "checksum"      : str(artifact_checksum),
            "label"         : str(artifact_label),
            "openchain"     : str(artifact_openchain),
            "action"        : str(action),
            "prev_block"    : str(prev),
            "cur_block"     : str(cur),
            "timestamp"     : str(timestamp),
            "artifact_list" : artifact_list,
            "uri_list"      : uri_list
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
            payload_sha512 = _sha512(payload),
            batcher_public_key = self._public_key,
            nonce = time.time().hex().encode()
        ).SerializeToString()

        signature = CryptoFactory(create_context("secp256k1")) \
            .new_signer(Secp256k1PrivateKey.from_hex(self._private_key)).sign(header)

        transaction = Transaction(
            header = header,
            payload = payload,
            header_signature = signature
        )
        
        # Creating batch list
        batch_list = self._create_batch_list([transaction])
        
        return self._send_request(
            "batches", batch_list.SerializeToString(),
            "application/octet-stream"
        )

    def _create_batch_list(self, transactions):
        """
        Helps create a batch list to be transmitted to the ledger.
        
        Args:
            transactions (list of Transaction): List containing transaction IDs
        
        Returns:
            type: BatchList
            BatchList object where each batch in the list are constructed in
            the function. 
            
        """
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key = self._public_key,
            transaction_ids = transaction_signatures
        ).SerializeToString()

        signature = CryptoFactory(create_context("secp256k1")) \
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
