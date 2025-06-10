# config.py
DB_CONFIG2 = {
    "host": "1.92.123.57",
    "port": 26000,
    "database": "postgres",
    "user": "daniel",
    "password": "Vivadios1@",
}

DB_CONFIG = {
    'host': '1.92.77.154', 
    'port': 26000,
    'database': 'network_security_research',
    'user': 'db_admin',
    'password': 'DBAdmin@SuperSecure!2024' 
}

import os

class Config:
    UPLOAD_FOLDER = '/home/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'docx', 'pdf'}
    OPEN_GAUSS_URI = "postgresql://newuser:newuser%40123@121.36.95.8:26000/shiyan"