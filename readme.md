# EDZ Web Application

This repository contains the Flask-based web application for EDZ.

# Setup

## Prerequisites

This project requires Python 3 or later.

## Cloning the Repository

To clone the repository, run the following command in your terminal:

```bash
git clone https://github.com/s-nasir/edzWeb.git
cd edzWeb/flask-server
```

## Setting Up the Python Virtual Environment

Once in /flask-server, create a python virtual environment

### Windows

```bash
python -m venv venv
```

To activate virtual environment

```bash
.\venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
```

To activate virtual environment

```bash
source venv/bin/activate
```

## Installing all dependencies

```bash
pip install -r requirements.txt
```

## Running the server

Once the virtual environment is activated, you can run the server using:

```bash
python ./server.py
```

or

```bash
python3 ./server.py
```

## Updating the Microsoft SQL Database Connection

```python
# Replace the placeholders with your database credentials
connection_string = 'DRIVER={SQL Server};SERVER=YOUR_HOST;DATABASE=YOUR_DB;UID=YOUR_USER-ID;PWD=YOUR_PASSWORD'
```

# Requirements Satisfied

- Backend Setup using Flask
- Used MS SQL for backend database
- Implemented Complete registration and login system
- Separate registration for coaches and users
- Common login for both user types
- Error handling
- Used Bootstrap for basic frontend
- Tested app on Postman, MSSMS (Microsoft SQL Server Management Studio)

## Hosted a demo on Render (had to migrate to postgre sql, since azure is paid)
Link: https://edz-render-demo.onrender.com/


- Postman Test for Coach Registration:
  ![](/imgs/postman-coach-register.jpg)

- Postman Test for User Registration:
  ![](/imgs/postman-user-register.jpg)

- Postman Test for Login:
  ![](/imgs/postman-login.jpg)

- MSSMS Database Screenshot
  ![](/imgs/sql-query-test.jpg)
