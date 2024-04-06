FROM --platform=amd64 python:3.10-slim

RUN apt-get update && \
    apt-get install -y git \
                       gcc g++ \
                       libffi-dev

# Update pip and setuptools
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade pip setuptools

RUN mkdir -p /opt/app
COPY requirements.txt /opt/app/requirements.txt
COPY app.py /opt/app
WORKDIR /opt/app

# app dependencies
RUN pip3 install -r requirements.txt

EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD ["app.py" ]
