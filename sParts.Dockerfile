FROM sameerfarooq/sparts-test:latest

ARG DEBIAN_FRONTEND=noninteractive
# FILES YOU WOULD LIKE TO COPY INTO THE IMAGE GOES HERE
COPY ./proto/register_user.py /project/src/register_user.py
COPY ./proto/lazy_user.py /project/src/lazy_user.py

COPY ./proto/tp_artifact_1.0/sawtooth_artifact/processor/handler.py /project/src/tp_artifact_1.0/sawtooth_artifact/processor/handler.py
COPY ./proto/tp_artifact_1.0/sawtooth_artifact/artifact_cli.py /project/src/tp_artifact_1.0/sawtooth_artifact/artifact_cli.py
COPY ./proto/tp_artifact_1.0/sawtooth_artifact/artifact_batch.py /project/src/tp_artifact_1.0/sawtooth_artifact/artifact_batch.py

COPY ./proto/tp_category_1.0/sawtooth_category/processor/handler.py /project/src/tp_category_1.0/sawtooth_category/processor/handler.py
COPY ./proto/tp_category_1.0/sawtooth_category/category_cli.py /project/src/tp_category_1.0/sawtooth_category/category_cli.py
COPY ./proto/tp_category_1.0/sawtooth_category/category_batch.py /project/src/tp_category_1.0/sawtooth_category/category_batch.py

COPY ./proto/tp_organization_1.0/sparts_organization/organization_cli.py /project/src/tp_organization_1.0/sparts_organization/organization_cli.py
COPY ./proto/tp_organization_1.0/sparts_organization/organization_batch.py /project/src/tp_organization_1.0/sparts_organization/organization_batch.py
COPY ./proto/tp_organization_1.0/sparts_organization/processor/handler.py /project/src/tp_organization_1.0/sparts_organization/processor/handler.py

COPY ./proto/tp_part_1.0/sawtooth_part/part_cli.py /project/src/tp_part_1.0/sawtooth_part/part_cli.py
COPY ./proto/tp_part_1.0/sawtooth_part/part_batch.py /project/src/tp_part_1.0/sawtooth_part/part_batch.py
COPY ./proto/tp_part_1.0/sawtooth_part/processor/handler.py /project/src/tp_part_1.0/sawtooth_part/processor/handler.py


COPY ./api/sparts-api.py /project/sparts-api.py

COPY ./proto/tp_part_1.0/sawtooth_part/part-api.py /project/src/tp_part_1.0/sawtooth_part/part-api.py
COPY ./proto/tp_organization_1.0/sparts_organization/organization-api.py /project/src/tp_organization_1.0/organization-api.py
COPY ./proto/tp_artifact_1.0/sawtooth_artifact/artifact-api.py /project/src/tp_artifact_1.0/sawtooth_artifact/artifact-api.py
COPY ./proto/tp_category_1.0/sawtooth_category/category-api.py /project/src/tp_category_1.0/sawtooth_category/category-api.py

COPY ./start_ledger/sparts_ledger.sh /project/ledger-startup-scripts/sparts_ledger.sh

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/* && \
    cd /project/src/tp_artifact_1.0 && \
    python3 setup.py install && \
    cd /project/src/tp_category_1.0 && \
    python3 setup.py install && \
    cd /project/src/tp_organization_1.0 && \
    python3 setup.py install && \
    cd /project/src/tp_part_1.0 && \
    python3 setup.py install
