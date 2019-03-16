# FROM sameerfarooq/sparts-test:latest
FROM phyohtut/sparts-test:part

# ARG DEBIAN_FRONTEND=noninteractive
# FILES YOU WOULD LIKE TO COPY INTO THE IMAGE GOES HERE
# COPY ./phyo/register_user.py /project/src/register_user.py
# COPY ./phyo/lazy_user.py /project/src/lazy_user.py

# COPY ./phyo/tp_category_1.0/sawtooth_category/processor/handler.py /project/src/tp_category_1.0/sawtooth_category/processor/handler.py
# COPY ./phyo/tp_category_1.0/sawtooth_category/category_cli.py /project/src/tp_category_1.0/sawtooth_category/category_cli.py
# COPY ./phyo/tp_category_1.0/sawtooth_category/category_batch.py /project/src/tp_category_1.0/sawtooth_category/category_batch.py

# COPY ./phyo/tp_organization_1.0/sparts_organization/organization_cli.py /project/src/tp_organization_1.0/sparts_organization/organization_cli.py
# COPY ./phyo/tp_organization_1.0/sparts_organization/organization_batch.py /project/src/tp_organization_1.0/sparts_organization/organization_batch.py
# COPY ./phyo/tp_organization_1.0/sparts_organization/processor/handler.py /project/src/tp_organization_1.0/sparts_organization/processor/handler.py

# COPY ./phyo/tp_part_1.0/sawtooth_part/part_cli.py /project/src/tp_part_1.0/sawtooth_part/part_cli.py
# COPY ./phyo/tp_part_1.0/sawtooth_part/part_batch.py /project/src/tp_part_1.0/sawtooth_part/part_batch.py
# COPY ./phyo/tp_part_1.0/sawtooth_part/processor/handler.py /project/src/tp_part_1.0/sawtooth_part/processor/handler.py

# RUN apt-get update && \
#     apt-get install -y curl && \
#     rm -rf /var/lib/apt/lists/* && \
#     cd /project/src/tp_category_1.0 && \
#     python3 setup.py install && \
#     cd /project/src/tp_organization_1.0 && \
#     python3 setup.py install && \
#     cd /project/src/tp_part_1.0 && \
#     python3 setup.py install
