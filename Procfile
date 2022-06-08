# Configuration file for staging on Heroku
# Note that runtime.txt defines the python version used for Heroku,
# where we have chosen Python 3.6.9 as that is the version running
# on production at LANL

release: python test/genSecurityFile.py && python manage.py migrate --database=live
web: daphne LANE_server.asgi:application