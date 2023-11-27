# Flask-login-MYSQL

This is a simple Flask application to register and login (for development).

## Requirements

- Python 3.7 or higher
- Flask 1.1.2 or higher

## Installation

### Create virtual environment
```
pip install virtualenv
python -m venv venv
```

### Activated environment
```
source venv/bin/activate
```

### configuration database and another in "app/__init__.py"
```
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://userdb:passworddb@localhost/database_name'
app.config['TEMPLATES_AUTO_RELOAD'] = True #if dont need you can change to False
app.config['SECRET_KEY'] = 'secret_key'
```

### for generate secret_key with python
```
>>> import os
>>> os.urandom(12).hex()
```

### Install Package
```
pip install -r requirements.txt
```

### Init Database and Migrate
```
flask db init
flask db migrate
flask db upgrade
```

### run application
```
flask run -h 0.0.0.0
```

you can access in http://localhost:5000