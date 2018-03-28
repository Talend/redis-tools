FROM python:alpine
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
RUN python setup.py install

CMD ["redis-tools"]
