FROM pymesh/pymesh

RUN apt-get install -u zip
RUN pip3 install click

RUN mkdir /code
WORKDIR /code

COPY scale_mesh.py /code/
COPY make_bundle.py /code/
