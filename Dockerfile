FROM python:3.7

RUN pip install pipenv

ADD https://github.com/tianon/gosu/releases/download/1.11/gosu-amd64 /bin/gosu
RUN chmod +x /bin/gosu

WORKDIR /app

# Since the virtualenv is installed in the user directory for root, make this readable
RUN chmod a+rX /root

ADD . /app
RUN python -m pip install .

ENTRYPOINT ["/app/entrypoint"]

