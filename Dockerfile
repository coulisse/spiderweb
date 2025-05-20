# Build stage
FROM python:3.13-alpine AS builder

# Install build and runtime dependencies
# mariadb-connector-c-dev is required to compile the Python connector
RUN apk update && \
    apk upgrade --available && \
    apk add --no-cache --virtual .build-deps \
    gcc musl-dev linux-headers libev-dev sqlite-dev python3-dev mariadb-connector-c-dev && \
    apk add --no-cache \
    libev sqlite

# Configure environment variables for the build
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Clean up build dependencies. Here we remove .build-deps,
# but native libraries like libmariadb.so.3 (if they had been installed directly
# from a mariadb-connector-c package in the build stage) would have been removed.
# In our case, mariadb-connector-c-dev only provides headers and development libraries.
# The actual runtime library will be installed in the final stage.
RUN apk del .build-deps && \
     rm -rf /var/cache/apk/* /tmp/* /var/tmp/* /usr/share/man /etc/apk/cache/*

# Final (runtime) stage
FROM python:3.13-alpine

# Copy environment variables from the builder
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

WORKDIR /app

# Copy only what's necessary from the build stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app

# Install only the runtime dependencies needed for operation
# mariadb-connector-c provides libmariadb.so.3
# mariadb-client is for client utilities; you might not need it in the final container if you only use the Python connector
RUN apk update && \
    apk upgrade --available && \
    apk add --no-cache \
    libev sqlite mariadb-connector-c

RUN addgroup -S spiderweb_group && \
    adduser -S -G spiderweb_group -h /home/spiderweb_user spiderweb_user

EXPOSE 8080

CMD ["python", "-u", "wsgi.py"]