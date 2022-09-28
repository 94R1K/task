FROM nikolaik/python-nodejs:python3.9-nodejs16-alpine

WORKDIR /app

COPY . .
COPY ./Server ./app/Server
COPY ./WebClient ./app/WebClient
COPY ./script ./app/script
COPY ./requirements.txt ./app/requirements.txt

RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN python -m venv venv
RUN chmod +x ./venv/bin/activate
RUN ./venv/bin/activate
RUN python -m pip install -r ./requirements.txt

RUN touch run.sh
RUN echo -e "sh -c \"python WorkerScript/main.py;\" & sh -c \"cd Server; python manage.py runserver [::]:8080\" & sh -c \"cd WebClient; npm start;\"" > run.sh
RUN chmod +x run.sh

CMD ["sh", "run.sh"]
