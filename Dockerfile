FROM --platform=linux/amd64 python:3.10-slim

# System dependencies
RUN apt-get update && \
    apt-get install -y git \
                       gcc g++ \
                       libffi-dev
RUN apt-get update -y -qq && \
    apt-get install -y -qq \
        cmake \
        libopenmpi-dev \
        python3-dev \
        zlib1g-dev \
        libgl1-mesa-glx \
        swig
# Update pip and setuptools
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade pip setuptools wrds swig
# Install Gunicorn
RUN pip3 install gunicorn

RUN mkdir -p /opt/app
COPY requirements.txt /opt/app/requirements.txt
COPY api/. /opt/app
WORKDIR /opt/app

# app dependencies
RUN pip3 install -r requirements.txt

# Install FinRL from GitHub
RUN pip install git+https://github.com/AI4Finance-Foundation/FinRL.git

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]