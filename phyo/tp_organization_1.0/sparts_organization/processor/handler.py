
# Copyright 2017 Wind River Systems
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
from collections import OrderedDict
# from sawtooth_sdk.processor.state import StateEntry
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
# from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.processor.handler import TransactionHandler

LOGGER = logging.getLogger(__name__)
################################################################################
#                               HANDLER OBJ                                    #
################################################################################
class OrganizationTransactionHandler:
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'organization'

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
            (org_id, org_alias, org_name, org_type, description, org_url, 
                action, part_id, timestamp) = transaction.payload.decode() \
                .split(",")
            
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")

        validate_transaction(org_id, action)
               
        data_address = make_organization_address(self._namespace_prefix, org_id)
        
        state_entries = context.get_state([data_address])
        
        if len(state_entries) != 0:
            try:

                stored_organization_id, stored_organization_str = \
                state_entries[0].data.decode().split(",",1)

                stored_organization = json.loads(stored_organization_str)
                
            except ValueError:
                raise InternalError("Failed to deserialize data.")
            
        else:
            stored_organization_id = stored_organization = None
            
        if action == "create" and stored_organization_id is not None:
            raise InvalidTransaction("Invalid Action-organization already exists.")
    
        if action == "create":
            organization = create_organization(org_id, org_alias, org_name, 
                                org_type, description, org_url, timestamp)
            stored_organization_id = org_id
            stored_organization = organization
            _display("Created an organization.")
        
        if action == "AddPart":
            if part_id not in stored_organization_str:
                organization = add_part(part_id,stored_organization)
                stored_organization = organization  
            
        # Put data back in state storage
        stored_org_str = json.dumps(stored_organization)
        data=",".join([stored_organization_id,stored_org_str]).encode()
        addresses = context.set_state({data_address:data})
        
        return addresses

def add_part(uuid, parent_organization):    
    organization_list = parent_organization['parts']
    organization_dic = {'part_id': uuid}
    organization_list.append(organization_dic)
    parent_organization['parts'] = organization_list
    return parent_organization    

def create_organization(org_id, org_alias, org_name, org_type, 
                            description, org_url, timestamp):
    
    return {'organization_id' : org_id, 'organization_alias' : org_alias, 
            'organization_name' : org_name, 'type' : org_type, 
            'description' : description, 'organization_url' : org_url, 
            'parts' : [], 'timestamp' : timestamp} 

def validate_transaction(org_id, action):
    if not org_id:
        raise InvalidTransaction('Organization ID is required') 
    if not action:
        raise InvalidTransaction('Action is required')

    if action not in ('create', "AddPart"):
        raise InvalidTransaction('Invalid action: {}'.format(action))

def make_organization_address(namespace_prefix, org_id):
    return namespace_prefix + \
        hashlib.sha512(org_id.encode('utf-8')).hexdigest()[:64]

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
