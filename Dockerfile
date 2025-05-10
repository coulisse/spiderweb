#FROM python:3.13
FROM python:3.13-slim-bookworm  

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    libev-dev gcc \
    locales \
    sqlite3 libsqlite3-0 libmariadb-dev \
    mariadb-client && \
    locale-gen en_US.UTF-8 && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN groupadd --system spiderweb_group && \
    useradd --system --gid spiderweb_group --home-dir /home/spiderweb_user spiderweb_user

EXPOSE 8080

CMD ["python", "-u", "wsgi.py"]
