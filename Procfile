# Configuration file for staging on Heroku
# Note that runtime.txt defines the python version used for Heroku,
# and requirements.txt defines the python dependencies
#
# Note that heroku dynamically assigns a port, cannot default to 8000

web: daphne -p $PORT LANE_server.asgi:application