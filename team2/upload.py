import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, make_response,send_file
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2 import sql
from config import Config
import io
# 检查文件类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


DB_CONFIG = {
    'host': '1.92.77.154',
    'port': '26000',
    'dbname': 'network_security_research',
    'user': 'db_admin',
    'password': 'DBAdmin@SuperSecure!2024'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
def get_file_from_db(file_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_data, filename FROM files WHERE id = %s", (file_id,))
    file_data, filename = cursor.fetchone()
    conn.close()
    return file_data, filename

# 初始化数据库并创建表
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    category TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# 保存文件信息到数据库
# 将文件以 BLOB 格式存储到数据库
def save_file_to_db_blob(filename, category, file_content, file_type, **kwargs):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO files 
            (filename, category, file_type, file_data, name, student_id, teacher_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (filename,
             category,
             file_type,
             psycopg2.Binary(file_content),
             kwargs.get('name'),
             kwargs.get('student_id'),
             kwargs.get('teacher_id')))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# 获取指定类别的文件
def get_files_by_category(category):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, filename FROM files WHERE category=%s ORDER BY upload_time DESC", (category,))
    files = c.fetchall()
    conn.close()
    return files

# 获取指定文件的路径
def get_file_path(file_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT filename, file_path FROM files WHERE id=%s", (file_id,))
    file_info = c.fetchone()
    conn.close()
    return file_info[1] if file_info else None  # 返回file_path
