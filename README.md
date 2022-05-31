# LANE server

### 1. Getting started

Begin by cloning the repository:

```
git clone https://github.com/dougUCN/LANE-server.git
```

### 2. Setting up a virtual environment:

In the root directory

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
python3 -m pip install -r dependencies.txt
```

### 3. Generating a secret key

In the root directory, with venv enabled, run

```
python test/genSecurityFile.py # --debug True <-- Only use this flag if in development!
```

**SECURITY WARNING: keep the secret key used in production secret!**

**SECURITY WARNING: don't run with debug turned on in production!**

### 4. Generate the live database

In the root directory, with venv enabled, run

```bash
python manage.py migrate --database=live
```

### 5. Running the server

In the root directory, with venv enabled, run the following command to start the server:

```
daphne LANE_server.asgi:application
```

Basic queries can now be tested at the graphql endpoint, located at

http://127.0.0.1:8000/graphql/

# Contributing

See the [contribution guidelines](CONTRIBUTING.md)