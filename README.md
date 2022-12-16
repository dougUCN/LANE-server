# LANE server

### 1. Getting started

Begin by cloning the repository:

```
git clone https://github.com/dougUCN/LANE-server.git
```

### 2. Setting up a virtual environment:

In the LANE-server directory

```
python3 -m venv venv
source venv/bin/activate # Starts the venv
```

Update pip to the latest version:

```
python3 -m pip install --upgrade pip
```

Install dependencies

```
python3 -m pip install -r requirements.txt
```

**Note**: On the production server, upgrading pip and starting the venv breaks the environment variable established by `export http_proxy=http://proxyout.lanl.gov:8080`, leading to some `SSL: CERTIFICATE` errors on the `pip install` step. Simply rerun the `export` command and then proceed with dependency installation as described.

### 3. Generating a secret key

In the LANE-server directory, with venv enabled, run

```
python scripts/genSecurityFile.py # --debug True <-- Only use this flag if in development!
```

**SECURITY WARNING: keep the secret key used in production secret!**

**SECURITY WARNING: don't run with debug turned on in production!**

And add these lines to your `~/.bashrc` file

```
### LANE Server debug flag and secret key
if [ -f ${path_to_LANE_server}/LANE_server/.security ]; then
    . ${path_to_LANE_server}/LANE_server/.security
fi
```

Then, to propagate these changes and reactivate the venv, in the LANE-server directory run

```
source ~/.bashrc
source venv/bin/activate
```

### 4. Running the server

In the LANE-server directory, with venv enabled, run the following command to start the server:

```
daphne LANE_server.asgi:application
```

Basic queries can now be tested at the graphql endpoint, located at

http://127.0.0.1:8000/graphql/

# Live Demo

See the live demo [here](https://lane-server.herokuapp.com/graphql/)!

# Contributing

See the [contribution guidelines](CONTRIBUTING.md)
