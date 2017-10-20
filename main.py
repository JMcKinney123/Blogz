from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dsfhsad;ufoids7t98ugklchvxckj'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'a_blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        existing_user = User.query.filter_by(username=username).first()
        error_password = ""
        error_username = ""
        
        if user and user.password != password:
            error_password = "Username and password do not match!"
        if not existing_user:
            error_username = "Username does not exist."
        if username == "":
            error_username = "Username blank!"
        if password == "":
            error_password = "Password blank!"
        if user and user.password == password:
            session['username'] = username
            return render_template("add_new_blog.html")
        else:
            return render_template("login.html", error_password=error_password, error_username=error_username)
    return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        error_username = ""
        error_password = ""
        error_verify = ""
        
        for i in username:
            if i.isspace():
                error_username = "Error: No spaces allowed in username."
        if username == "":
            error_username = "Error: Username is blank."
        elif len(username) < 3 or len(username) > 20:
            error_username = "Error: Username must be between 3 and 20 characters."
            username = ""
        for i in password:
            if i.isspace():
                error_password = "Error: No spaces allowed in password."
        if password == "":
            error_password = "Error: Password is blank."
        elif len(password) < 3 or len(password) > 20:
            error_password = "Error: Password must be between 3 and 20 characters."
            password = ""
        
        if verify == "":
            error_verify = "Error: Verification must match password."
        elif verify != password:
            error_verify = "Error: Verification must match password." 
            verify = ""
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_username = "Username already exists!"
        
        if not error_username and not error_password and not error_verify and not existing_user:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else: 
            return render_template("signup.html", error_username=error_username, error_password=error_password, error_verify=error_verify)
        
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    del session ['username']
    return redirect('/blog')


@app.route('/')
def index():
    
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route("/blog", methods=['GET'])
def a_blog():

        blog_id =  request.args.get('id')
        user_id = request.args.get('userid')
        blogs = Blog.query.all()
        
        if blog_id:
            blog = Blog.query.filter_by(id=blog_id).first()
            return render_template("one_blog.html", title=blog.title, body=blog.body, user=blog.owner.username, user_id=blog.owner_id)
        if user_id:
            owner_id = user_id
            posts = Blog.query.filter_by(owner_id=user_id).all()
            return render_template('singleUser.html', posts=posts)
        return render_template('blog.html', blogs=blogs)
    

@app.route("/newpost", methods=["POST", "GET"])
def addnewpost():
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']
        
        error = ""
        error_too = ""
        if new_title == "":
            error = "Error, title required for blog."          
        
        if new_body == "":
            error_too = "Error, body is blank."
        
        if error or error_too:
            return render_template("add_new_blog.html", error=error, error_too=error_too)
        else:
            blog = Blog(new_title, new_body, owner)
            db.session.add(blog)
            db.session.commit()
            blog_listing = "/blog?id=" + str(blog.id)
            return redirect(blog_listing)
    return render_template("add_new_blog.html")
 


if __name__ == '__main__':
    app.run()