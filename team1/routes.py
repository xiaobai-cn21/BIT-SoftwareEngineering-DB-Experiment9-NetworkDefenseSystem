from flask import Blueprint, render_template
from .getInformation import getInformation

team1_bp = Blueprint('team1', __name__)

# 动态数据库 schema
user_schema = "user_schema"
education_schema = "education_schema"
achievement_schema = "achievement_schema"

@team1_bp.route('/fullTimeTeacher')
def page1():
    sqlQuery = f"""
        SELECT * FROM {schema}.teacher t 
        INNER JOIN {schema}.full_time_teacher f ON t.teacher_id = f.teacher_id;
    """
    teacherInfo = getInformation(sqlQuery)
    return render_template('team1/full_time_teacher.html', teacherInfo=teacherInfo)

@team1_bp.route('/partTimeTeacher')
def page2():
    sqlQuery = f"""
        SELECT * FROM {schema}.teacher t
        INNER JOIN {schema}.part_time_teacher f ON t.teacher_id = f.teacher_id;
    """
    teacherInfo = getInformation(sqlQuery)
    return render_template('team1/part_time_teacher.html', teacherInfo=teacherInfo)

@team1_bp.route('/actualStudents')
def page3():
    sqlQuery = f"SELECT * FROM {schema}.student;"
    studentInfo = getInformation(sqlQuery)
    return render_template('team1/actual_students.html', studentInfo=studentInfo)

@team1_bp.route('/student_card/<int:student_id>')
def page4(student_id):
    sqlQuery = f"SELECT * FROM {schema}.student WHERE student_id = %s;"
    student_info = getInformation(sqlQuery, (student_id,))
    return render_template('team1/student_card.html', student_info=student_info[0])

@team1_bp.route('/gradStudents')
def page5():
    sqlQuery = f"SELECT * FROM {schema}.student WHERE category='毕业';"
    studentInfo = getInformation(sqlQuery)
    return render_template('team1/graduated_students.html', studentInfo=studentInfo)

@team1_bp.route('/gradStudent_card/<int:student_id>')
def page6(student_id):
    sqlQuery = f"""
        SELECT * FROM {schema}.student s
        INNER JOIN {schema}.graduated_student g ON s.student_id = g.student_id 
        WHERE s.student_id = %s;
    """
    student_info = getInformation(sqlQuery, (student_id,))
    return render_template('team1/grad_student_card.html', student_info=student_info[0])

@team1_bp.route('/teacherCourse')
def page7():
    sqlQuery = f"""
        SELECT c.course_id, c.course_name, c.course_id, c.level,
               STRING_AGG(t.name, ', ') AS teachers
        FROM {education_schema}.course c
        LEFT JOIN {education_schema}.teaching_work tw ON c.course_id = tw.course_id
        LEFT JOIN {user_schema}.teacher t ON tw.teacher_id = t.teacher_id
        GROUP BY c.course_id, c.course_name, c.level;
    """
    courseInfo = getInformation(sqlQuery)
    return render_template('team1/teacher_course.html', courseInfo=courseInfo)

@team1_bp.route('/teacherReasearch')
def page8():
    sqlQuery = f"""
        SELECT * FROM {education_schema}.research_work r
        INNER JOIN {user_schema}.teacher t ON r.teacher_id = t.teacher_id;
    """
    queryInfo = getInformation(sqlQuery)
    return render_template('team1/teacher_research.html', queryInfo=queryInfo)

@team1_bp.route('/researchResult')
def page9():
    return render_template('team1/research_result.html')

@team1_bp.route('/patentResult')
def page10():
    sqlQuery = f"SELECT * FROM {achievement_schema}.patent;"
    queryInfo = getInformation(sqlQuery)
    return render_template('team1/patent_result.html', patentInfo=queryInfo)

@team1_bp.route('/textbookResult')
def page11():
    sqlQuery = f"""
        SELECT t.name, STRING_AGG(tb.name, ',') AS writers
        FROM {achievement_schema}.textbook t
        JOIN {achievement_schema}.teacher_textbook tb ON tb.textbook_id = t.textbook_id
        GROUP BY t.name;
    """
    queryInfo = getInformation(sqlQuery)
    return render_template('team1/textbook_result.html', textbookInfo=queryInfo)

@team1_bp.route('/reformResult')
def page12():
    return render_template('team1/reformResult.html')

@team1_bp.route('/international_information')
def page13():
    return render_template('team1/international_information.html')
