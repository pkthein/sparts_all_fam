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
import logging
import json
from datetime import datetime
from collections import OrderedDict
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.handler import TransactionHandler

LOGGER = logging.getLogger(__name__)
################################################################################
#                               HANDLER OBJ                                    #
################################################################################
class ArtifactTransactionHandler:
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'artifact'

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def encodings(self):
        return ['csv-utf8']

    @property
    def namespaces(self):
        return [self._namespace_prefix]
################################################################################
#                                 FUNCTIONS                                    #
################################################################################
    def apply(self, transaction, context):

        try:
            # The payload is csv utf-8 encoded string
            payload = json.loads(transaction.payload.decode())
            artifact_id             = payload["artifact_id"]
            artifact_alias          = payload["artifact_alias"]
            artifact_name           = payload["artifact_name"]
            artifact_type           = payload["artifact_type"]
            artifact_checksum       = payload["artifact_checksum"]
            artifact_label          = payload["artifact_label"]
            artifact_openchain      = payload["artifact_openchain"]
            action                  = payload["action"]
            prev                    = payload["prev_block"]
            cur                     = payload["cur_block"]
            timestamp               = payload["timestamp"]
            
            # artifact_list
            # sub_artifact_id         = payload["sub_artifact_id"]
            # path                    = payload["path"]
            artifact_list           = payload["artifact_list"]
            
            # uri_list
            # artifact_version        = payload["artifact_version"]
            # artifact_checksum_uri   = payload["artifact_checksum_uri"]
            # content_type            = payload["content_type"]
            # size                    = payload["size"]
            # uri_type                = payload["uri_type"]
            # location                = payload["location"]
            uri_list                = payload["uri_list"]
            
            
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        validate_transaction(artifact_id, action)
               
        data_address = make_artifact_address(self._namespace_prefix, artifact_id)
          
        state_entries = context.get_state([data_address])
       
        if len(state_entries) != 0:
            try:
                
                stored_artifact = state_entries[0].data.decode()
                stored_artifact_id = stored_artifact["artifact_id"]
                             
            except ValueError:
                raise InternalError("Failed to deserialize data.")
 
        else:
            stored_artifact_id = stored_artifact = None
            
        # 3. Validate the artifact data
        if action == "create" and stored_artifact_id is not None:
            raise InvalidTransaction("Invalid Action-artifact already exists.")
        
        elif action == "create":
            artifact = create_artifact(artifact_id, artifact_alias, 
                            artifact_name, artifact_type, artifact_checksum, 
                            artifact_label, artifact_openchain, 
                            prev, cur, timestamp)
        elif action == "amend" and stored_artifact_id is not None:
            artifact = create_artifact(artifact_id, artifact_alias, 
                            artifact_name, artifact_type, artifact_checksum, 
                            artifact_label, artifact_openchain, 
                            prev, cur, timestamp, 
                            artifact_list, uri_list)
        elif action == "AddArtifact" or action == "AddURI":
            if stored_artifact_id is None:
                raise InvalidTransaction(
                    "Invalid Action-requires an existing artifact."
                )
            artifact = create_artifact(artifact_id, artifact_alias, 
                            artifact_name, artifact_type, artifact_checksum, 
                            artifact_label, artifact_openchain, 
                            prev, cur, timestamp, 
                            artifact_list, uri_list)
            
        data = json.dumps(artifact).encode()
        addresses = context.set_state({data_address:data})
       
        return addresses
        
# def add_artifact(uuid,parent_artifact,path):
    
#     artifact_list = parent_artifact['artifact_list']
#     artifact_dic = {'artifact_id': uuid,'path':path}
#     artifact_list.append(artifact_dic)
#     parent_artifact['artifact_list'] = artifact_list  
#     return parent_artifact     

# def add_URI(artifact,version,artifact_checksum,content_type,size,uri_type,location):
   
#     URI_list = artifact['uri_list']
#     URI_dic = {'version': version,'checksum': artifact_checksum,'content_type': content_type,'size':size,'uri_type':uri_type,'location':location}      
#     URI_list.append(URI_dic)
#     artifact['uri_list'] = URI_list
#     return artifact

def create_artifact(artifact_id, artifact_alias, artifact_name, artifact_type, 
                    artifact_checksum, artifact_label, artifact_openchain, 
                    prev, cur, timestamp, artifact_list=[], uri_list=[]):
    return {    
                "artifact_id"           : artifact_id,
                "artifact_alias"        : artifact_alias,
                "artifact_name"         : artifact_name,
                "artifact_type"         : artifact_type,
                "artifact_checksum"     : artifact_checksum,
                "artifact_label"        : artifact_label,
                "artifact_openchain"    : artifact_openchain,
                "prev_block"            : prev, 
                "cur_block"             : cur,
                "timestamp"             : timestamp,
                "artifact_list"         : artifact_list,
                "uri_list"              : uri_list
            }


def validate_transaction( artifact_id, action):
    if not artifact_id:
        raise InvalidTransaction('Artifact ID is required')
    
    if not action:
        raise InvalidTransaction('Action is required')

    if action not in ("AddArtifact", "create", "AddURI", "amend"):
        raise InvalidTransaction('Invalid action: {}'.format(action))

def make_artifact_address(namespace_prefix, artifact_id):
    return namespace_prefix + \
        hashlib.sha512(artifact_id.encode('utf-8')).hexdigest()[:64]

def _display(msg):
    n = msg.count("\n")

    if n > 0:
        msg = msg.split("\n")
        length = max(len(line) for line in msg)
    else:
        length = len(msg)
        msg = [msg]

    LOGGER.debug("+" + (length + 2) * "-" + "+")
    for line in msg:
        LOGGER.debug("+ " + line.center(length) + " +")
    LOGGER.debug("+" + (length + 2) * "-" + "+")
################################################################################
#                                                                              #
################################################################################
