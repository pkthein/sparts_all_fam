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
import logging
import json
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.handler import TransactionHandler

LOGGER = logging.getLogger(__name__)
################################################################################
#                               HANDLER OBJ                                    #
################################################################################
class PartTransactionHandler:
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'pt'

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
            pt_id       = payload["pt_id"]
            pt_name     = payload["pt_name"]
            checksum    = payload["pt_checksum"]
            version     = payload["pt_version"]
            alias       = payload["pt_alias"]
            licensing   = payload["pt_licensing"]
            label       = payload["pt_label"]
            description = payload["description"]
            action      = payload["action"]
            prev        = payload["prev_block"]
            cur         = payload["cur_block"]
            timestamp   = payload["timestamp"]
            artifact_id = payload["artifact_id"]
            category_id = payload["category_id"] 
            supplier_id = payload["supplier_id"]
            
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")
        
        validate_transaction( pt_id,action)  
             
        data_address = make_part_address(self._namespace_prefix, pt_id)
        
        state_entries = context.get_state([data_address])
     
        if len(state_entries) != 0:
            try:
                   
                    stored_pt_str = state_entries[0].data.decode()
                    stored_pt = json.loads(stored_pt_str)
                    stored_pt_id = stored_pt["pt_id"]
                    
            except ValueError:
                raise InternalError("Failed to deserialize data.")
        
        else:
            stored_pt_id = stored_pt = None
      
        if action == "create" and stored_pt_id is not None:
            raise InvalidTransaction("Invalid part already exists.")

        elif (action == "AddArtifact" or action == "AddSupplier" 
                or action == "AddCategory"):
            if stored_pt_id is None:
                raise InvalidTransaction(
                    "Invalid the operation requires an existing part."
                )
        elif action == "create":
            pt = create_part(pt_id, pt_name, checksum, version, alias, 
                    licensing, label, description, prev, cur, timestamp)
            _display("Created a part.")
        elif action == "amend" and stored_pt_id is not None:
            pt = create_part(pt_id, pt_name, checksum, version, alias, 
                    licensing, label, description, prev, cur, timestamp, 
                    artifact_id, category_id, supplier_id)
            _display("Amended a category.")
        elif action == "AddArtifact":
            if artifact_id not in stored_pt_str:
                pt = add_artifact(artifact_id, stored_pt)
        elif action == "AddSupplier":
            if supplier_id not in stored_pt_str:
                pt = add_supplier(supplier_id, stored_pt)
        elif action == "AddCategory":
            if category_id not in stored_pt_str:
                pt = add_category(category_id, stored_pt)
         
        # 6. Put data back in state storage
        data = json.dumps(pt).encode()
        addresses = context.set_state({data_address:data})

        return addresses

def add_artifact(uuid,parent_pt):
    
    pt_list = parent_pt['artifacts']
    pt_dic = {'artifact_id': uuid}
    pt_list.append(pt_dic)
    parent_pt['artifacts'] = pt_list
    return parent_pt  

def add_supplier(uuid,parent_pt):
    
    pt_list = parent_pt['suppliers']
    pt_dic = {'supplier_id': uuid}
    pt_list.append(pt_dic)
    parent_pt['suppliers'] = pt_list
    return parent_pt     

def add_category(uuid,parent_pt):
    
    pt_list = parent_pt['categories']
    pt_dic = {'category_id': uuid}
    pt_list.append(pt_dic)
    parent_pt['categories'] = pt_list
    return parent_pt        

def create_part(pt_id, pt_name, checksum, version, alias, licensing, label, 
                description, prev, cur, timestamp, artifact_id=[], 
                category_id=[], supplier_id=[]):
    return {
                "pt_id"         : pt_id,
                "pt_name"       : pt_name,
                "pt_checksum"   : checksum, 
                "pt_version"    : version, 
                "pt_alias"      : alias, 
                "pt_licensing"  : licensing, 
                "pt_label"      : label, 
                "description"   : description,
                "prev_block"    : prev,
                "cur_block"     : cur,
                "timestamp"     : timestamp,
                "artifact_id"   : artifact_id,
                "category_id"   : category_id,
                "supplier_id"   : supplier_id 
                
            }

def validate_transaction( pt_id,action):
    if not pt_id:
        raise InvalidTransaction('Part ID is required')
 
    if not action:
        raise InvalidTransaction('Action is required')

    if action not in ("AddArtifact", "create", "AddCategory", "AddSupplier", 
                        "list-part", "retrieve", "amend"):
        raise InvalidTransaction('Invalid action: {}'.format(action))

def make_part_address(namespace_prefix, part_id):
    return namespace_prefix + \
        hashlib.sha512(part_id.encode('utf-8')).hexdigest()[:64]

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
