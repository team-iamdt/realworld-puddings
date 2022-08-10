FROM openpolicyagent/opa:latest

ARG CONFIG_FILE_PATH='./docker/opa/config.yaml'

COPY $CONFIG_FILE_PATH /config.yaml

CMD ["run", "--server", "--log-level=info", "--log-format=text", "--config-file=/config.yaml"]
