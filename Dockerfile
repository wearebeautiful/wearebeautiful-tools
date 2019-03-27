FROM metabrainz/python:3.6

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
                       build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

RUN pip3.6 install setuptools uwsgi

RUN mkdir /code/wearebeautiful.info
WORKDIR /code/wearebeautiful.info

COPY . /code/wearebeautiful.info
RUN pip3.6 install -r requirements.txt

CMD uwsgi --gid=www-data --uid=www-data --http-socket :3031 \
          --vhost --module=app --callable=app --chdir=/code/wearebeautiful.info/wearebeautiful \
          --enable-threads --processes=10
