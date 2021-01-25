FROM python:3.9-alpine3.12

# Add default apk repositories for alpine 3.12
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.12/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.12/community" >> /etc/apk/repositories

# Update the repository and install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

WORKDIR /app

ENV PORT=5000

# Copy source files to container
COPY *.py ./
COPY requirements.txt .
COPY dist ./dist

# Run pip
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn --bind 0.0.0.0:$PORT run:app"]