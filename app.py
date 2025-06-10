from flask import Flask, render_template
from team1.routes import team1_bp
from team2.routes import team2_bp
from team3.routes import team3_bp


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 首页
@app.route('/')
def index():
    return render_template("main_page.html")

app.register_blueprint(team1_bp, url_prefix='/team1')
app.register_blueprint(team2_bp, url_prefix='/team2')
app.register_blueprint(team3_bp, url_prefix='/team3')



if __name__ == "__main__":
    app.run(debug=True)
