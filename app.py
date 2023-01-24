from email import message
from flask import *
import sqlite3 as sql
from random import randint
import datetime
from flask.helpers import url_for
from face_detection import *
import smtplib
import random
import string

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/upload'
app.secret_key = 'any random string'



@app.route("/")
def index():
    def random_with_N_digits(n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)
    a=random_with_N_digits(10)
    return render_template("index.html",a= a)
@app.route("/register",methods=['POST','GET'])
def register():
    if request.method == 'POST':
        voter_id = request.form['voterid']
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        password1 = request.form['pas1']
        password2 = request.form['pas2']
        dob = request.form['dob']
        mobile = request.form['phone']
        aadhar = request.form['aadhar']
        area = request.form['area']
        gender = request.form['gender']
        current_date = datetime.date.today()
        year = int(current_date.strftime('%Y'))
        given_date = int(dob[0:4])
        if (year-given_date) >= 18:
            if password1 == password2:
                val = face_register(voter_id)
                print(val)
                if val == 'already registered':
                    error = 'already registered'
                    return render_template("index.html",register_error=error)
                elif val=='success':
                    con = sql.connect('vote.db')
                    cur = con.cursor()
                    cur.execute('insert into register(Voter_Id,Name,Address,Mail,Password,DOB,Phone_Number,Aadhar_Number,Area,Gender) values(?,?,?,?,?,?,?,?,?,?)',(voter_id,name,address,email,password1,dob,mobile,aadhar,area,gender))
                    con.commit()

            else:
                field = [voter_id,name,address,email,password1,dob,mobile,aadhar,area,gender]
                value = 'Password Mismatch'
                return render_template("index.html",password_error=value,a=voter_id,field = field)
        else:
            field = [voter_id,name,address,email,dob,mobile,aadhar,area,gender]
            value = 'You are not eligible to vote'
            return render_template("index.html",age_error=value,a=voter_id,field=field)
    return render_template("index.html")

@app.route('/admin_dash',methods=['POST','GET'])
def admin_dash():
    from datetime import datetime
    minute = session['minute']
    hour = session['hour']
    key = session['screat']
    print(key)
    print(minute)
    if request.method == 'POST':
        no = request.form['screat']
        # no = no1.strip()
        # print('key',no)
        now = datetime.now()
        current_hour = now.strftime("%H")
        current_minute = now.strftime("%M")
        print(current_minute)
        if int(current_hour) == int(hour) and int(current_minute) <=(int(minute)+20):
            print(no)
            if str(key) == str(no):
                return render_template("admin_dash.html")
            else:
                screat_error = 'Invalid Screact Number'
                return render_template("admin.html",screat_error=screat_error)
        else:
            time_error = 'Time Out'
            return render_template("admin.html",time_error=time_error)
    
    return render_template("admin.html")
    

@app.route("/login",methods=['POST','GET'])
def login():
    print()
    from datetime import datetime
    if request.method == 'POST':
        voter_id = request.form['voter_id']
        password = request.form['password']
        session['voter_id'] = voter_id
        if voter_id == "1234567891011" and password == "admin":
            def random_with_N_digits(n):
                range_start = 10**(n-1)
                range_end = (10**n)-1
                return randint(range_start, range_end)
            screat_no=random_with_N_digits(10)
            session['screat'] = screat_no
            s=smtplib.SMTP('smtp.gmail.com: 587')
            s.starttls()
            frommail = 'officerbank909@gmail.com'
            s.login('officerbank909@gmail.com','bank1000')
            message = "Subject: Your Screat Key \n"+str(screat_no)
            # message = a1 + a2
            to_mail = 'shahana.retech@gmail.com'
            s.sendmail(frommail,to_mail,message)
            s.quit()
            now = datetime.now()
            hour = now.strftime("%H")
            minute = now.strftime("%M")
            session['minute'] = minute
            session['hour'] = hour
            # admin_dash(current_hour,minute,screat_no) 
            return redirect(url_for('admin_dash'))
            # return render_template("admin_dash.html")
        else:
            con = sql.connect("vote.db")
            cur = con.cursor()
            res = cur.execute('select Voter_Id,Password from register where Voter_Id=? and Password=?',(voter_id,password))
            data = res.fetchone()
            con.commit()
            print(data)
            if data:
                con = sql.connect("vote.db")
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("select * from election_date")   
                rows = cur.fetchall()
                con.commit()
                return render_template('vote.html',row=rows)
            else:
                error = 'Invalid User Details'
                return render_template('login.html',error=error)
    return render_template("login.html")       

@app.route('/candidates',methods=['POST','GET'])
def candidates():
    if request.method == 'POST':
        doc = request.files['file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'],doc.filename)
        print(doc.filename)
        doc.save(filepath)
        con = sql.connect('vote.db')
        cur = con.cursor()
        with open('static/upload/'+doc.filename,'r')as file:
            no_records = 0
            for row in file:
                cur.execute("insert into candidates(Name,Age,Gender,Address,EMail,Mobile,Area,Party) values(?,?,?,?,?,?,?,?)",row.split(','))
                con.commit()
                no_records += 1
    return render_template('admin_dash.html')

@app.route("/view_candidate",methods=['POST','GET'])
def view_candidate():
    con = sql.connect("vote.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from candidates")   
    rows = cur.fetchall()
    con.commit()
    return render_template("view_candidate.html",row = rows)

@app.route("/view_voter_details",methods=["POST","GET"])
def view_voter_details():
    con = sql.connect("vote.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from register")   
    rows = cur.fetchall()
    con.commit()
    return render_template("view_voter_details.html",row = rows)
@app.route("/election_assign",methods=["POST","GET"])
def election_assign():
    if request.method=='POST':
        date = request.form['date']
        election = request.form['election']
        print(date)
        current_date = datetime.date.today()
        year =current_date.strftime('%Y,%m,%d')
        curent_date = date.split('-')
        year = year.split(',')
        if curent_date >= year:
            print(year)
            con = sql.connect('vote.db')
            cur = con.cursor()
            cur.execute('insert into election_date(Date,Election) values(?,?)',(date,election))
            con.commit()
            return render_template('election_assign.html')
        else:
            error= 'error'
            return render_template('election_assign.html',error=error)
    return render_template('election_assign.html')

@app.route('/election_view',methods=['POST','GET'])   
def election_view():
    con = sql.connect("vote.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from election_date")   
    rows = cur.fetchall()
    con.commit()
    return render_template("election_view.html",row = rows)

@app.route('/election_remove/<string:type>',methods=['POST','GET'])   
def election_remove(type):
    print(type)
    con = sql.connect("vote.db")
    # con.row_factory = sql.Row
    cur = con.cursor()
    if type == 'election':
        cur.execute("delete from election_date")   
    elif type == 'candidate':
        cur.execute("delete from candidates")   
    rows = ''
    con.commit()
    return render_template("election_view.html",row = rows)


@app.route('/polling',methods=['POST','GET'])
def polling():
    con = sql.connect("vote.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from register")   
    rows = cur.fetchall()
    con.commit()
    return render_template('polling.html',row=rows)

if '__main__' == __name__:
    app.run(debug=True)
