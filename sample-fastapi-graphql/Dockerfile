FROM python:3.10-alpine3.16:builder

COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
RUN cd /app \
    && apk add --update --no-cache build-base gcc libffi-dev musl-dev curl \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python \
    && rm -rf /var/lib/apt/lists/* \
    && source $HOME/.poetry/env \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev -n -v

FROM python:3.10-alpine3.16

COPY ./ /app/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /root/.poetry /root/.poetry

WORKDIR /app
ENTRYPOINT ["python"]
CMD ["fastapi_gql/server.py", "run"]
