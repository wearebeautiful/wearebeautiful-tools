# wearebeautiful.info

The code that powers our main website.


## To setup a sandbox:

virtualenv -p python3 .ve
source .ve/bin/activate
pip3 install -r requirements.txt

## To prepare to run the sandbox
docker rm -f wab-redis ; docker run --name wab-redis -p 6379:6379 -d redis
export FLASK_APP=wearebeautiful/app.py
export FLAK_ENV=development
export FLASK_DEBUG=1
export FLASK_RUN_HOST=0.0.0.0

## run it!
flask run
