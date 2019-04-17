#!/bin/bash
nohup /project/ledger-startup-scripts/start_validator.sh &
sleep 3s
nohup /project/ledger-startup-scripts/start_sawtooth_rest_api.sh &
sleep 2s
#nohup /project/ledger-startup-scripts/poet_validator.sh &
#sleep 2s
nohup /project/ledger-startup-scripts/settings_tp.sh &
sleep 2s	
nohup /project/ledger-startup-scripts/tp_category_family.sh &
sleep 2s
nohup /project/ledger-startup-scripts/tp_artifact_family.sh &
sleep 2s
nohup /project/ledger-startup-scripts/tp_organization_family.sh &
sleep 2s
nohup /project/ledger-startup-scripts/tp_part_family.sh &
sleep 2s
nohup /project/ledger-startup-scripts/tp_user_family.sh &
sleep 2s
nohup /usr/bin/python3 /project/sparts-api.py &
sleep 2s
nohup /usr/bin/python3 /project/src/tp_category_1.0/sawtooth_category/category-api.py &
sleep 2s
nohup /usr/bin/python3 /project/src/tp_organization_1.0/sparts_organization/organization-api.py &
sleep 2s
nohup /usr/bin/python3 /project/src/tp_part_1.0/sawtooth_part/part-api.py &
sleep 2s
nohup /usr/bin/python3 /project/src/tp_artifact_1.0/sawtooth_artifact/artifact-api.py &
sleep 2s
