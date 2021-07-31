from enum import unique
from flask import Flask,redirect,url_for,render_template,request,g
from flask.globals import session
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null
import pymysql
pymysql.install_as_MySQLdb()
from flask import session
import json
from werkzeug.utils import secure_filename


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SQLALCHEMY_POOL_RECYCLE"] = 280
db = SQLAlchemy(app)
app.secret_key = 'super secret key'
class Userinfo(db.Model):
    sno=db.Column(db.Integer,primary_key = True)
    firstname = db.Column(db.String(20),nullable=False)
    lastname = db.Column(db.String(20),nullable=False)
    dd=db.Column(db.Integer,nullable=False)
    mm=db.Column(db.Integer,nullable=False)
    yy=db.Column(db.Integer,nullable=False)
    country = db.Column(db.String(20),nullable=False)
    phone = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(50),nullable=False)
    username = db.Column(db.String(20),nullable=False)
    password = db.Column(db.String(20),nullable=False)
    bio =  db.Column(db.String(1000),nullable=True)
    proffession =db.Column(db.String(100),nullable=True)
    

class Img(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    img=db.Column(db.Text,nullable=False)
    name=db.Column(db.Text,nullable=False)
    mimetype=db.Column(db.Text,nullable=False)
    caption = db.Column(db.String(100),nullable=False)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
   if request.method=="POST":
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            dd = request.form.get("dd")
            mm = request.form.get("mm")
            yy = request.form.get("yy")
            country =  request.form.get("country")
            phone = request.form.get("phone")
            email =  request.form.get("email")
            username =  request.form.get("user")
            password =  request.form.get("pass")
            if Userinfo.query.filter_by(username=username).first():
               flash("Username already exists","danger")
            elif len(password) <8:
                flash("Password too Short","danger")
            elif Userinfo.query.filter_by(phone=phone).first():
                flash("Phone Number already Exists")
            elif len(phone)<10 or len(phone)>11:
                flash("Phone Number Not Valid","danger")
            elif Userinfo.query.filter_by(email=email).first():
                flash("Email already Exists","danger")
            
            else:
                EntryToDatabase = Userinfo(firstname =fname,
                lastname=lname,dd=dd,mm=mm,yy=yy,
                country=country,phone=phone
                ,email=email,username=username,
                password=password) 
                db.session.add (EntryToDatabase)
                db.session.commit()
                flash("Account Created Successfully Now You Can Log in","success")
                return redirect("/")
   allinfo=Userinfo.query.all()   
    
   return render_template("signup.html",allinfo=allinfo)

@app.route("/", methods=['GET', 'POST'])
def login():
    if g.user: # agar user session me h to 
        users =  Userinfo.query.filter(Userinfo.username.like(g.user)).all()
        allinfo = Userinfo.query.all()                        
        return render_template('Home.html',allinfo=allinfo,users=users)
            
    if request.method=='POST':
        username = request.form.get('user')
        userpass = request.form.get('passwd')
        print(f"from form data {username} {userpass}")
        #if (username ==params['admin_user'] and userpass ==params['admin_password']):
        #unam =  db.session.execute("SELECT username FROM userinfo WHERE username=:username{'username':username}").fetchone()
        #passw = db.session.execute("SELECT password FROM userinfo WHERE username=username{'username':username}").fetchone()  
        #print(passw[0])
        unam = Userinfo.query.filter_by(username=username).first()
        upas = Userinfo.query.filter_by(password=userpass).first()
        if unam is not None and upas is not None :
            if username==unam.username  and userpass==unam.password:
                #set the session variable
                session['user'] = username
                users = Userinfo.query.filter(Userinfo.username.like(username)).all()
                allinfo = Userinfo.query.all()
                return render_template('Home.html',allinfo=allinfo,users=users)
     
        else:
            flash("Incorrect Username Or Password","danger")


    return render_template('index.html')


@app.route('/logout')
def logout():
   session.pop("user")
   flash("You are Logged Out ","danger")
   return redirect("/")
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print(g.user)
    if g.user:
    #g.user me current user sotred h 
       results = Userinfo.query.filter(Userinfo.username.like(g.user)).all()
    return render_template("profile.html",allinfo=results)

@app.before_request
def before_request():
    g.user=None
    if "user" in session:
        g.user=session["user"]
@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if g.user:
        if request.method=='POST':
            pic = request.files.get("pic")
            caption = request.form.get("caption")
            if not pic:
                flash("Select a Picture","danger")
            filename = secure_filename(pic.filename)
            mimetype=pic.mimetype
            img = Img(img=pic.read(),mimetype=mimetype,name=filename,caption=caption)
            db.session.add(img)
            db.session.commit()
        flash("uploaded successfully","success")
    return redirect("/")
@app.route('/update', methods=['GET', 'POST'])
def ProfileUpdate():
   if g.user:
       print(g.user)
       if request.method=="POST":
            fname = request.form.get("fname")
            lname = request.form.get("lname")
            password = request.form.get("pass")
            password2 = request.form.get("pass2")
            Data=Userinfo.query.filter_by(username=g.user).first()
            if Data.password==password2:
                bio = request.form.get("bio")
                proffession = request.form.get("prfsn")
                Dataupdate =  Userinfo.query.filter_by(username=g.user).first()
                print(Dataupdate)
                Dataupdate.firstname=fname
                Dataupdate.lastname=lname
                Dataupdate.password=password
                Dataupdate.bio = bio
                Dataupdate.proffession=proffession
                db.session.add(Dataupdate)
                db.session.commit()
                allinfo=  Userinfo.query.filter(Userinfo.username.like(g.user)).all()
                flash("Profile Details Updated","success")
                return render_template("profile.html",allinfo=allinfo)
            else:
                flash("Password Did Not Match Or Incorrect Password","danger")
       allinfo=  Userinfo.query.filter(Userinfo.username.like(g.user)).all()
       return render_template("profileupdate.html",allinfo=allinfo)

@app.route('/active', methods=['GET', 'POST'])
def active_user():
        print(session)
        return render_template("uf.html",session=session)
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
     app.run(port=5000,debug=True)
