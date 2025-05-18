#FROM python:3.13-slim-bookworm  
#
#RUN apt-get update && \
#    apt-get upgrade -y && \
#    apt-get install -y --no-install-recommends \
#    libev-dev gcc \
#    locales \
#    sqlite3 libsqlite3-0 libmariadb-dev \
#    mariadb-client && \
#    locale-gen en_US.UTF-8 && \
#    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
#    dpkg-reconfigure --frontend=noninteractive locales \
#    && apt-get clean \
#    && rm -rf /var/lib/apt/lists/* 
#
#ENV LANG=en_US.UTF-8
#ENV LANGUAGE=en_US:en
#ENV LC_ALL=en_US.UTF-8
#
#WORKDIR /app
#
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . .
#
#RUN groupadd --system spiderweb_group && \
#    useradd --system --gid spiderweb_group --home-dir /home/spiderweb_user spiderweb_user
#
##last clean
#RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
#
#EXPOSE 8080
#
#CMD ["python", "-u", "wsgi.py"]



FROM python:3.13-alpine

RUN apk update && \
    apk upgrade --available && \
    apk add --no-cache --virtual .build-deps \
    gcc musl-dev linux-headers libev-dev sqlite-dev python3-dev && \
    apk add --no-cache \
    libev mariadb-client sqlite 

RUN apk add --no-cache mariadb-connector-c-dev

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S spiderweb_group && \
    adduser -S -G spiderweb_group -h /home/spiderweb_user spiderweb_user

#last clean
RUN apk del .build-deps && \
    rm -rf /var/cache/apk/* /tmp/* /var/tmp/*

EXPOSE 8080

CMD ["python", "-u", "wsgi.py"]