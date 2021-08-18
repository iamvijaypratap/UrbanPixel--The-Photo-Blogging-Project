from enum import unique
from flask import Flask,redirect,url_for,render_template,request,g
from flask.globals import session
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null,desc
import pymysql
from sqlalchemy.sql.expression import desc
pymysql.install_as_MySQLdb()
from flask import session
import json
from werkzeug.utils import secure_filename
from random import *
from flask_mail import * 
from flask_mail import Message
from flask_mail import Mail
import hashlib


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app=Flask(__name__)
mail = Mail(app)  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = 'nreply760@gmail.com'  
app.config['MAIL_PASSWORD'] = 'Vijay@26101996'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
mail = Mail(app)  
otp = randint(000000,999999)  #this will genrerate a random 6 digit OTP
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/urbanpixel'
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
    password = db.Column(db.String(150),nullable=False)
    bio =  db.Column(db.String(1000),nullable=True)
    proffession =db.Column(db.String(100),nullable=True)
    

class Img(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    img=db.Column(db.Text,nullable=True)
    name=db.Column(db.Text,nullable=True)
    mimetype=db.Column(db.Text,nullable=False)
    caption = db.Column(db.String(100),nullable=False)
    user = db.Column(db.String(50),nullable=False)

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
            hashed_pass = hashlib.md5(password.encode())
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
                password=hashed_pass.hexdigest()) 
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
        img = Img.query.all()        
        return render_template('Home.html',allinfo=allinfo,users=users,img=img)
            
    if request.method=='POST':
        username = request.form.get('user')
        userpass = request.form.get('passwd')
        hashed_userpass = hashlib.md5(userpass.encode())
        print(f"from form data {username} {hashed_userpass.hexdigest()}")
        #if (username ==params['admin_user'] and userpass ==params['admin_password']):
        #unam =  db.session.execute("SELECT username FROM userinfo WHERE username=:username{'username':username}").fetchone()
        #passw = db.session.execute("SELECT password FROM userinfo WHERE username=username{'username':username}").fetchone()  
        #print(passw[0])
        unam = Userinfo.query.filter_by(username=username ).first()
        upas = Userinfo.query.filter_by(password=hashed_userpass.hexdigest()).first()
        if unam is not None and upas is not None :
            if username==unam.username and hashed_userpass.hexdigest()==unam.password:
                #set the session variable
                session['user'] = username
                users = Userinfo.query.filter(Userinfo.username.like(username)).all()
                allinfo = Userinfo.query.all()
                img = Img.query.all()
                return render_template('Home.html',allinfo=allinfo,users=users,img=img)
     
        else:
            flash("Incorrect Username Or Password","danger")


    return render_template('index.html')


@app.route('/logout')
def logout():
   session.pop("user")
   flash("You are Logged Out ","danger")
   return redirect("/")
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method=="POST":
        user = request.form.get("user")
        result = Userinfo.query.filter_by(username=user).first()
        if result is not None:
            session["user"]=user
            #print(result.email)
            #print(user)
            msg = Message('OTP',sender = 'nreply760@gmail.com', recipients = [result.email])  
            msg.body = f" A request has been recieved to change the password for your UrbanPixel Account your secret otp is {str(otp)}" 
            mail.send(msg) 
            flash(f"hello {result.username} a otp has been sent you registered email id {result.email}","success")
            return render_template("otp_valid.html")
        else:
            flash("UserName Does Not Exists","danger")

    return render_template("reset.html")
@app.route('/otp_validation', methods=['GET', 'POST'])
def otp_validation():
   if g.user:
        print(g.user)
        if request.method=="POST":
            user_otp = request.form.get("otp1")
            if user_otp==str(otp):
                return render_template("pw.html")
            else:
                flash("OTP doesn't Match","danger")
                return render_template("otp_valid.html")
@app.route('/password', methods=['GET', 'POST'])
def password():
   if g.user:
       if request.method=="POST":
           ps = hashlib.md5(request.form.get("ps").encode())
           ps1  = hashlib.md5(request.form.get("ps1").encode())
           if ps.hexdigest()==ps1.hexdigest():
                Dataupdate =  Userinfo.query.filter_by(username=g.user).first()
                print(Dataupdate)
                Dataupdate.password=ps1.hexdigest()
                db.session.add(Dataupdate)
                db.session.commit()
                return render_template("index.html")
           else:
                flash("Password Doesnt Match","danger")
                return render_template("pw.html")
          

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print(g.user)
    if g.user:
    #g.user me current user sotred h 
       results = Userinfo.query.filter(Userinfo.username.like(g.user)).all()
       user =  Userinfo.query.filter_by(username=g.user).first()
       contents = Img.query.filter(Img.user.like(user.username)).all()
       print(contents)
    return render_template("profile.html",allinfo=results,contents=contents)

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
            user =  Userinfo.query.filter_by(username=g.user).first()
            img = Img(img=pic.read(),mimetype=mimetype,name=filename,caption=caption,user=user.username)
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
            password = hashlib.md5(request.form.get("pass").encode())
            password2 = hashlib.md5(request.form.get("pass2").encode())
            Data=Userinfo.query.filter_by(username=g.user).first()
            if Data.password==password2.hexdigest():
                bio = request.form.get("bio")
                proffession = request.form.get("prfsn")
                Dataupdate =  Userinfo.query.filter_by(username=g.user).first()
                print(Dataupdate)
                Dataupdate.firstname=fname
                Dataupdate.lastname=lname
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
@app.route('/userprofile/<int:sno>')
def userprofile(sno):
    if g.user:
       users = Userinfo.query.filter(Userinfo.username.like(g.user)).all()
       up = Userinfo.query.filter(Userinfo.sno.like(sno)).all()
       return render_template("uf.html",up=up,users=users)
@app.route('/user_profile/<string:user>')
def user_profile(user):
    if g.user:
        users = Userinfo.query.filter(Userinfo.username.like(g.user)).all()
        up = Userinfo.query.filter(Userinfo.username.like(user)).all()
        contents = Img.query.filter(Img.user.like(user)).all()
        return render_template("uf.html",contents=contents,up=up,users=users)
    

@app.route('/active', methods=['GET', 'POST'])
def active_user():
        print(session)
        return render_template("uf.html",session=session)
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
     app.run(port=5000,debug=True)
