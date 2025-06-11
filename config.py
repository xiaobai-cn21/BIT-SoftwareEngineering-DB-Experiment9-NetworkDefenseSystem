from dotenv import load_dotenv
import os

# 加载.env文件中的变量到os.environ
load_dotenv()

DB_CONFIG = {
    'host': os.environ.get('DB_HOST'), 
    'port': os.environ.get('DB_PORT'),
    'database': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'), 
}

import os

class Config:
    UPLOAD_FOLDER = '/home/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'docx', 'pdf'}
    OPEN_GAUSS_URI = "postgresql://newuser:newuser%40123@121.36.95.8:26000/shiyan"