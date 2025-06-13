from flask import Blueprint, render_template, redirect, url_for
from flask import Flask, render_template, request, jsonify, session
from flask import Flask, send_file,render_template, request, jsonify, session
import psycopg2
import os
import io
from config import Config
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from .upload import get_file_from_db,get_file_path,get_files_by_category,save_file_to_db_blob,init_db,allowed_file
team2_bp = Blueprint('team2', __name__)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}

DB_CONFIG = {
    'host': '1.92.77.154',
    'port': '26000',
    'dbname': 'network_security_research',
    'user': 'db_admin',
    'password': 'DBAdmin@SuperSecure!2024'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
@team2_bp.route('library')
def page3():
    if 'user_name' not in session:
        return redirect(url_for('team3.login_page'))
    return render_template('team2/library.html')


@team2_bp.route('search_books', methods=['POST'])
def page4():
      # 获取查询参数
        keyword = request.form.get('keyword', '').strip()

        # 构建查询语句
        query = "SELECT * FROM library_schema.book WHERE 1=1"
        params = []

        if keyword:
            query += " AND title LIKE %s OR book_id LIKE %s"
            params.extend([f"%{keyword}%", f"%{keyword}%"])

            # 执行查询
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(query, params)
            books = cur.fetchall()

            # 将查询结果转换为字典列表
            columns = [desc[0] for desc in cur.description]
            books_list = [dict(zip(columns, row)) for row in books]

            return jsonify(books_list)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

        finally:
            cur.close()
            conn.close()


@team2_bp.route('/borrow_books', methods=['GET'])
def page5():
    # 从session获取用户名
    user_name = session.get('chinese_name', None)
    if not user_name:
        return jsonify({'error': '用户未登录'}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 查询借阅记录
        query ="""
    SELECT book.title, 
           TO_CHAR(borrow_record.borrow_time, 'YYYY-MM-DD HH24:MI:SS') AS borrow_time,
           TO_CHAR(borrow_record.due_time, 'YYYY-MM-DD HH24:MI:SS') AS due_time,
           CASE 
               WHEN CURRENT_DATE < borrow_record.due_time THEN '借阅中'
               ELSE '已归还' 
           END AS status
    FROM library_schema.borrow_record
    JOIN library_schema.book ON borrow_record.title = book.title
    WHERE borrow_record.user_name = %s
    ORDER BY borrow_record.borrow_time DESC
    """
        cur.execute(query, (user_name,))
        records = cur.fetchall()

        # 转换为字典列表
        columns = [desc[0] for desc in cur.description]
        records_list = [dict(zip(columns, row)) for row in records]

        # 查询借阅总数
        cur.execute("SELECT COUNT(*) FROM library_schema.borrow_record WHERE user_name = %s", (user_name,))
        total_records = cur.fetchone()[0]

        return jsonify({
            'total': total_records,
            'records': records_list
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@team2_bp.route('/borrow_books', methods=['POST'])
def page6():
    book_id = request.form.get('book_id')
    # 从session获取用户名
    user_name = session.get('chinese_name', None)
    title = request.form.get('title')
    if not user_name:
        return jsonify({'success': False, 'message': '用户未登录'}), 401
    if not book_id:
        return jsonify(success=False, message="书籍ID缺失"), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 检查书籍状态
        cur.execute("SELECT is_borrowed FROM library_schema.book WHERE book_id = %s", (book_id,))
        status = cur.fetchone()[0]

        if status == 'false':
            return jsonify({'success': False, 'message': '书籍当前不可借阅'}), 400

        # 更新书籍状态
        cur.execute("UPDATE library_schema.book SET is_borrowed = 'true' WHERE book_id = %s", (book_id,))

        # 添加借阅记录
        cur.execute("""
                    INSERT INTO library_schema.borrow_record (borrow_id, user_name,title, borrow_time, due_time)
                    VALUES (%s, %s, %s,CURRENT_DATE, CURRENT_DATE + INTERVAL '30 days')
                    """, (book_id, user_name,title))

        conn.commit()
        return jsonify({'success': True, 'message': '借阅成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@team2_bp.route('/uploads', methods=['GET'])
def page7():
    if request.method == 'POST':
        # 检查文件部分
        if 'file' not in request.files:
            return '没有选择文件', 400
        file = request.files['file']

        # 验证文件
        if file.filename == '':
            return '没有选择文件', 400

        # 获取表单数据
        file_type = request.form.get('file_type')
        category = request.form.get('category')

        # 验证必填字段
        if not file_type:
            return '请选择文件类型', 400
        if not category:
            return '请选择资料分类', 400

        # 验证分类相关字段
        extra_args = {}
        if category in ['开题资料', '中期资料', '答辩资料', '学位论文']:
            if not request.form.get('name') or not request.form.get('student_id'):
                return '请填写姓名和学号', 400
            extra_args = {
                'name': request.form['name'],
                'student_id': request.form['student_id']
            }
        elif category == '专利资料':
            if not request.form.get('name') or not request.form.get('teacher_id'):
                return '请填写姓名和工号', 400
            extra_args = {
                'name': request.form['name'],
                'teacher_id': request.form['teacher_id']
            }

        # 保存文件
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_content = file.read()

            save_file_to_db_blob(
                filename=filename,
                category=category,
                file_content=file_content,
                file_type=file_type,
                **extra_args
            )

            return redirect(url_for('browse_files', category=category))

    return render_template('team2/uploads.html')


@team2_bp.route('/files/<category>')
def page8(category):
    files = get_files_by_category(category)
    return render_template('team2/files.html', category=category, files=files)

@team2_bp.route('/download/<int:file_id>')
def page9(file_id):
    # 获取文件数据和文件名
    file_data, filename = get_file_from_db(file_id)

    # 将 BLOB 数据转换为 docx 文件
    docx_filename = filename if filename.endswith('.docx') else filename + '.docx'

    # 使用 io.BytesIO 将 BLOB 数据存储到内存中
    file_stream = io.BytesIO(file_data)

    # 返回文件给客户端，提供下载
    return send_file(file_stream, as_attachment=True, download_name=docx_filename,
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@team2_bp.route('/download_all')
def page10():
    categories = ['开题资料', '中期资料', '答辩资料', '学位论文', '专利资料', '会议资料', '上级文件', '其他资料']
    return render_template('team2/categories.html', categories=categories)

