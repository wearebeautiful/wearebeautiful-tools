FROM pymesh/pymesh

RUN apt-get update && apt-get install -y zip imagemagick 
RUN pip3 install --upgrade pip
RUN pip3 install numpy && pip3 install click scipy numpy matplotlib peewee python-dateutil
RUN pip3 install git+https://github.com/wearebeautiful/stl_tools.git#egg=stl_tools

WORKDIR /code/wab
