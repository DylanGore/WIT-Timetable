FROM joyzoursky/python-chromedriver:3.8-alpine3.10

WORKDIR /app

ENV PORT=5000

# Copy source files to container
COPY *.py ./
COPY requirements.txt .
COPY timetable.json .
COPY dist ./dist

# Run pip
RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:$PORT run:app