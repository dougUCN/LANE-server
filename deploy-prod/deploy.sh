#!/bin/bash

echo "Stopping supervisord"
supervisorctl stop all

echo "Jump to app folder"
cd $HOME/LANE/LANE-server
pwd

git checkout -- deploy-prod/deploy.sh
git pull

echo "Check for any dependency updates"
source venv/bin/activate
export https_proxy=http://proxyout.lanl.gov:8080
pip install -r requirements.txt

echo "Restart supervisord"
supervisorctl start all
