from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

team3_bp = Blueprint('team3', __name__)

def md5_hash(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()

@team3_bp.route('/')
def team3_home():
    return "Team 3 Blueprint is working!"


# 用户登录接口
@team3_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')  # 前端传来的中文

        # user_type_map 用于映射
        user_type_map = {'教师': 'teacher', '学生': 'student', '图书管理员': 'admin'}

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, password, user_type, chinese_name FROM user_schema.users WHERE username=%s AND user_type=%s",
            (username, user_type)
        )
        row = cur.fetchone()
        if not row or row[1] != md5_hash(password):
            cur.close()
            conn.close()
            return jsonify({'msg': '用户名或密码错误'}), 401
        user_id, _, _, chinese_name = row

        session['user_id'] = user_id
        session['username'] = username
        session['user_type'] = user_type_map[user_type]
        session['chinese_name'] = chinese_name
        session['user_name'] = chinese_name

        if user_type == '学生':
            cur.execute("SELECT grade, category, program_type, supervisor, nationality, is_part_time, is_international, is_suspended, notes FROM user_schema.student WHERE student_id=%s", (username,))
            stu_row = cur.fetchone()
            print('学生信息:', stu_row)
            if stu_row:
                session['grade'] = stu_row[0]
                session['category'] = stu_row[1]
                session['program_type'] = stu_row[2]
                session['supervisor'] = stu_row[3]
                session['nationality'] = stu_row[4]
                session['is_part_time'] = stu_row[5]
                session['is_international'] = stu_row[6]
                session['is_suspended'] = stu_row[7]
                session['notes'] = stu_row[8]
        elif user_type == '教师':
            cur.execute("SELECT college, title, degree_level, status, teacher_type, notes FROM user_schema.teacher WHERE teacher_id=%s", (username,))
            tea_row = cur.fetchone()
            if tea_row:
                session['college'] = tea_row[0]
                session['title'] = tea_row[1]
                session['degree_level'] = tea_row[2]
                session['status'] = tea_row[3]
                session['teacher_type'] = tea_row[4]
                session['notes'] = tea_row[5]

        cur.close()
        conn.close()
        return jsonify({'msg': '登录成功', 'user_id': user_id, 'username': username, 'user_type': user_type, 'chinese_name': chinese_name})
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 方便调试
        return jsonify({'msg': f'服务器错误: {str(e)}'}), 500

# 教师注册接口
@team3_bp.route('/register/teacher', methods=['POST'])
def register_teacher():
    data = request.json
    # 用户表 NOT NULL 字段
    required_fields = [
        'username', 'password', 'user_type', 'chinese_name',
        'college', 'status', 'degree_level', 'teacher_type'
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({'msg': f'缺少字段: {field}'}), 400
    # 校验选项合法性
    if data['teacher_type'] not in ['全职', '兼职']:
        return jsonify({'msg': '教师类型必须为全职或兼职'}), 400
    if data['degree_level'] not in ['博士', '硕士', '学士']:
        return jsonify({'msg': '学位层次不合法'}), 400
    if data['status'] not in ['在职', '离职', '退休']:
        return jsonify({'msg': '状态不合法'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    # 检查users表
    cur.execute("SELECT user_id FROM user_schema.users WHERE username=%s", (data['username'],))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'msg': '该工号已注册'}), 400
    cur.execute("SELECT teacher_id FROM user_schema.teacher WHERE teacher_id=%s", (data['username'],))
    teacher_exists = cur.fetchone()
    hashed_pw = md5_hash(data['password'])
    cur.execute(
        "INSERT INTO user_schema.users (username, password, user_type, chinese_name, english_name, gender, birth_date, mobile_phone, email) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING user_id",
        (data['username'], hashed_pw, data['user_type'], data['chinese_name'], data['english_name'],
         data.get('gender'), data.get('birth_date'), data['mobile_phone'], data['email'])
    )
    user_id = cur.fetchone()[0]
    # 插入/更新teacher表
    if teacher_exists:
        cur.execute(
            "UPDATE user_schema.teacher SET user_id=%s, name=%s, college=%s, notes=%s, status=%s, gender=%s, degree_level=%s, title=%s, teacher_type=%s WHERE teacher_id=%s",
            (user_id, data['chinese_name'], data['college'], data.get('notes'), data['status'], data.get('gender'), data['degree_level'], data.get('title'), data['teacher_type'], data['username'])
        )
    else:
        cur.execute(
            "INSERT INTO user_schema.teacher (user_id, teacher_id, name, college, notes, status, gender, degree_level, title, teacher_type) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (user_id, data['username'], data['chinese_name'], data['college'], data.get('notes'), data['status'], data.get('gender'), data['degree_level'], data.get('title'), data['teacher_type'])
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'msg': '注册成功'})

# 学生注册接口
@team3_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.json
    # 用户表 NOT NULL 字段
    required_fields = [
        'username', 'password', 'user_type', 'chinese_name',
        'grade', 'category', 'program_type', 'supervisor'
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({'msg': f'缺少字段: {field}'}), 400
    # 校验选项合法性
    if data['category'] not in ['在读', '毕业']:
        return jsonify({'msg': '类别必须为在读或毕业'}), 400
    if data['program_type'] not in ['工学博士', '工程博士', '学术硕士', '专业硕士']:
        return jsonify({'msg': '培养类型不合法'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    # 检查users表
    cur.execute("SELECT user_id FROM user_schema.users WHERE username=%s", (data['username'],))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'msg': '该学号已注册'}), 400
    cur.execute("SELECT student_id FROM user_schema.student WHERE student_id=%s", (data['username'],))
    student_exists = cur.fetchone()
    hashed_pw = md5_hash(data['password'])
    cur.execute(
        "INSERT INTO user_schema.users (username, password, user_type, chinese_name, english_name, gender, birth_date, mobile_phone, email) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING user_id",
        (
            data['username'], hashed_pw, data['user_type'], data['chinese_name'], data['english_name'],
            data.get('gender'), data.get('birth_date'), data['mobile_phone'], data['email']
        )
    )
    user_id = cur.fetchone()[0]
    if student_exists:
        cur.execute(
            "UPDATE user_schema.student SET user_id=%s, name=%s, grade=%s, category=%s, program_type=%s, supervisor=%s, nationality=%s, is_part_time=%s, is_international=%s, is_suspended=%s, notes=%s WHERE student_id=%s",
            (user_id, data['chinese_name'], data['grade'], data['category'], data['program_type'], data['supervisor'], data.get('nationality'), data.get('is_part_time', False), data.get('is_international', False), data.get('is_suspended', False), data.get('notes'), data['username'])
        )
    else:
        cur.execute(
            "INSERT INTO user_schema.student (user_id, student_id, name, grade, category, program_type, supervisor, nationality, is_part_time, is_international, is_suspended, notes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                user_id, data['username'], data['chinese_name'], data['grade'], data['category'], data['program_type'],
                data['supervisor'], data.get('nationality'),
                data.get('is_part_time', False), data.get('is_international', False), data.get('is_suspended', False),
                data.get('notes')
            )
        )
    if data['category'] == '毕业':
        cur.execute(
            "INSERT INTO user_schema.graduated_student (student_id, graduation_date, first_employer, enrollment_date) VALUES (%s, %s, %s, %s)",
            (data['username'], data.get('graduation_date'), data.get('first_employer'), data.get('enrollment_date'))
        )
    elif data['category'] == '在读':
        cur.execute(
            "INSERT INTO user_schema.current_student (student_id) VALUES (%s)",
            (data['username'],)
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'msg': '注册成功'})

@team3_bp.route('/auto_register', methods=['GET', 'POST'])
def auto_register():
    conn = get_db_connection()
    cur = conn.cursor()
    initial_password = '12345678'
    md5_pw = md5_hash(initial_password)
    # 自动注册教师
    cur.execute("SELECT teacher_id, name, college, status, degree_level, teacher_type FROM user_schema.teacher WHERE user_id IS NULL")
    teachers = cur.fetchall()
    teacher_count = 0
    for teacher_id, name, college, status, degree_level, teacher_type in teachers:
        username = teacher_id
        chinese_name = name
        user_type = '教师'
        cur.execute("SELECT user_id FROM user_schema.users WHERE username=%s", (username,))
        if cur.fetchone():
            continue
        cur.execute(
            "INSERT INTO user_schema.users (username, password, user_type, chinese_name) VALUES (%s, %s, %s, %s) RETURNING user_id",
            (username, md5_pw, user_type, chinese_name)
        )
        user_id = cur.fetchone()[0]
        cur.execute("UPDATE user_schema.teacher SET user_id=%s WHERE teacher_id=%s", (user_id, teacher_id))
        teacher_count += 1
    # 自动注册学生
    cur.execute("SELECT student_id, name, grade, category, program_type, supervisor FROM user_schema.student WHERE user_id IS NULL")
    students = cur.fetchall()
    student_count = 0
    for student_id, name, grade, category, program_type, supervisor in students:
        if not supervisor:
            continue  # 跳过没有导师的学生
        username = student_id
        chinese_name = name
        user_type = '学生'
        cur.execute("SELECT user_id FROM user_schema.users WHERE username=%s", (username,))
        if cur.fetchone():
            continue
        cur.execute(
            "INSERT INTO user_schema.users (username, password, user_type, chinese_name) VALUES (%s, %s, %s, %s) RETURNING user_id",
            (username, md5_pw, user_type, chinese_name)
        )
        user_id = cur.fetchone()[0]
        cur.execute("UPDATE user_schema.student SET user_id=%s WHERE student_id=%s", (user_id, student_id))
        student_count += 1
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'msg': f'自动注册完成，教师{teacher_count}人，学生{student_count}人，初始密码均为{initial_password}'})

@team3_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@team3_bp.route('/login')
def login_page():
    return render_template('team3/login.html')

@team3_bp.route('/register')
def register_page():
    return render_template('team3/register.html')

@team3_bp.route('/user_center')
def user_center():
    if not session.get('user_id'):
        return redirect(url_for('team3.login_page'))
    return render_template('team3/user_center.html')

