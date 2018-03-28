FROM python:3.6-alpine3.7
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt \
    && python setup.py install

CMD ["redis-tools"]
