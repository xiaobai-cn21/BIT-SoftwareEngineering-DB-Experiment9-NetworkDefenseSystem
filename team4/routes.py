from flask import Blueprint, render_template

team3_bp = Blueprint('team4', __name__)

@team3_bp.route('/page5')
def page5():
    return render_template('page5.html')

@team3_bp.route('/page6')
def page6():
    return render_template('page6.html')
