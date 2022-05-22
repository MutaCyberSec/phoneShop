import re
from flask_pymongo import PyMongo
import pymongo
import passlib
from passlib.context import CryptContext
from passlib.hash import argon2, bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
import smtplib
import random
from flask import  Flask, request , json , render_template,redirect,jsonify , redirect , url_for , request, redirect,flash,session
import requests
from datetime import datetime
import flask_mpesa
import socket
import base64
from requests.auth import HTTPBasicAuth
from flask_mpesa import MpesaAPI
from functools import wraps


app = Flask(__name__)

app.config["API_ENVIRONMENT"] = "sandbox"
app.config["APP_KEY"] = "TW1w1QUIjlIPu9Ig6xMEAVllxLqvlRby"  
app.config["APP_SECRET"] = "G5FpnkA7rdsvC4lw"

#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "loged_in" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('index'))
    return wrap


#log in session pop function
def pop_session(x):
    @wraps(x)
    def wrap(*args,**kwargs):
        if  not "loged_in" in session:
            return x(*args,**kwargs)
        else:
            session.pop('loged_in', None)
    return wrap

        

app.config['MONGO_DBNAME'] = 'the_shop'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/the_shop'
mongo = PyMongo(app)
#HASH sCHEMES
Hash_passcode = CryptContext(schemes="sha256_crypt",sha256_crypt__min_rounds=131072)
username_hash = CryptContext(schemes=["sha256_crypt","argon2"])
#databases
users = mongo.db.users
phones = mongo.db.phones
resets = mongo.db.reset

@app.route('/',methods=['POST','GET'])
def index():
    session.pop('loged_in', None)
    if request.method == 'POST':
        login_user = users.find_one({'name' : request.form['username']})      
        if login_user:
            form_pass = request.form['pass'].encode('utf-8')
            hashed_pass = login_user['password']         
            if Hash_passcode.verify(form_pass,hashed_pass):
                    if login_user['dep'] == 'user':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('my_acc'))
                    if login_user['dep'] == 'mkuu':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('mkuu'))
    return render_template('index.html')
@app.route('/login', methods=['POST','GET'])
def login():
    session.pop('loged_in', None)
    if request.method == 'POST':
        users = mongo.db.accounts
        login_user = users.find_one({'name' : request.form['username']})      
        if login_user:
            form_pass = request.form['pass'].encode('utf-8')
            hashed_pass = login_user['password']         
            if Hash_passcode.verify(form_pass,hashed_pass):
                    if login_user['dep'] == 'user':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('my_acc'))
                    if login_user['dep'] == 'mkuu':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('mkuu'))
    return render_template('login.html')
@app.route('/register', methods=['POST', 'GET'])
def register():
    session.pop('loged_in', None)
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            passcode = request.form['pass'] 
            dep = "user"
            email = request.form['email']
            hashpass = Hash_passcode.hash(passcode)
            user_id = random.randint(99990 , 999909)
            users.insert_one({'name' : request.form['username'], 'password' : hashpass, 
                              "user_id" : user_id ,'dep':dep,'email':email})
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')
@app.route('/reset_passw' , methods=['POST','GET'])
@login_required
def reset_passw():
    if request.method == 'POST':
        logged =  session['loged_in']
        user_in = users.find_one({'name' : logged})
        resets = mongo.db.reset
        user_in_reset = resets.find_one({'name' : logged})
        
        reset_code = request.form['code']
        
        old_pass = request.form['defau']
        
        new_pass1 = request.form['pass1']
        
        new_pass2 = request.form['pass2']
        
        if new_pass2 == new_pass1:
            code_in_db = user_in_reset['code']
            if reset_code  == code_in_db:
                new_password = Hash_passcode.hash(new_pass2)
                users.find_one_and_update({"name" : logged}  ,{ '$set' :  {"password": new_password}})
                return redirect (url_for('index'))
        else:
            return redirect(url_for('reset_passw' , mess =  "Passwords not Similler,Try again"))
    return render_template('reset_passw.html')
    
@app.route('/db_err' , methods=['POST','GET']) 
def db_err():
    return render_template('db_err.html')   
    
    return render_template('reset_passw.html')
ip = socket. gethostbyname(socket. gethostname())
ipst = str(ip)

#making Timestamp
now = datetime.now()
now_c = now.strftime("%Y%m%d%H%M%S")
new_time = str(now_c)
#mpesa variables
mpesa_api = MpesaAPI(app)

base_url =ipst + ":4000"
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
bs_shortcode = '174379'
password = bs_shortcode + passkey + new_time
ret = base64.b64encode(password.encode())
pd = ret.decode('utf-8')

consumer_key = app.config["APP_KEY"]
consumer_secret = app.config["APP_SECRET"]

api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def mpesa_token():
    mpesa_auth_url = ' https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    verify = (requests.get(mpesa_auth_url, auth = HTTPBasicAuth(consumer_key , consumer_secret))).json()
    tok = verify['access_token']
    return tok

@app.route('/' , methods=["POST"])
def home():
    
    return "Welcome home"

@app.route('/home2/' , methods=["GET" ,"POST"])
def home2():
    '''
    headers = {"Authorization" : "Bearer %s" %mpesa_token(),
                'Content-Type': 'application/json'
                }
    '''
    headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer pUZYReswbylV4QAONIwBc18fxU0T'
    }
    payload = {
    "BusinessShortCode": 174379,
    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjIwMTA0MTEwMDEx",
    "Timestamp": "20220104110011",
    "CheckoutRequestID": "ws_CO_040120221134452840",
    }
   
    response_from_auth = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query',json=payload,headers=headers)
   
    return response_from_auth.text.encode('utf8')
    
    
@app.route('/pay/' , methods=['GET', "POST" ])
def pay():
    age = 10
    if 10 == age:
            tok = mpesa_token()
            return render_template('tok.html' , tok = tok)
    
    return render_template('tok.html')

@app.route('/lipa_na_mpesa/' , methods = ['GET' ,'POST'])
def lipa_na_mpesa():   
    in_que = mongo.db.drugs
    tar = session['usr']
    def do_pay(number):
        amount = session['pr']
        #amount =  400
        headers = {"Authorization" : "Bearer %s" %mpesa_token(),
                    'Content-Type': 'application/json'
                    }
        
        reuest = {
        "BusinessShortCode": bs_shortcode,
        "Password": pd,
        "Timestamp": new_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": number,
        "PartyB": bs_shortcode,
        "PhoneNumber": number,
        "CallBackURL": "https://b437-197-248-246-149.ngrok.io/",
        "AccountReference": "Phone Repair Shop",
        "TransactionDesc": "Payments" 
    }
     
        response_from_auth = requests.post(api_url,json=reuest,headers=headers)
            
        if response_from_auth.status_code > 299:
                return{
                        "code" : response_from_auth.status_code ,
                        "success": False,
                        "message":"Sorry, something went wrong please try again later."
                    },400
            
        else:
             data_back = {
                    "data": json.loads(response_from_auth.text)
                },200
             in_que.find_one_and_delete({"name": tar})
             return redirect(url_for('success' , data = data_back))
         
    if request.method == 'POST':
        number = int(request.form['no'])
        return redirect('http://localhost:4000/lipa_na_mpesa/')
        #do_pay(number = number)    
         
    return render_template('bill.html')

@app.route('/success/' ,methods = ['POST','GET'])
def success():
    
    
    
    return render_template('suc.html')


#the mkuu Application And Routes
@app.route('/mkuu/' , methods = ["POST" , "GET"])
def mkuu():
    
    
    return render_template('admin.html')

@app.route('/add_phone/' , methods = ["POST" , "GET"])
def add_phone():
    now = datetime.now()
    now_c = now.strftime("%Y %m %d %H %M %S ")
    if request.method == 'POST':
        
        owner = request.form['owner']
        
        owner_number = request.form['number']
        
        brand = request.form['brand']
        
        model = request.form['model']
        
        date = now_c
        
        title = request.form['title']
        
        desc = request.form['desc']
        
        cause = request.form['cause']
        
        spec_id = md5_crypt.hash(owner_number)
        
        
        phones.insert_one({"owner" : owner , "owner_number" : owner_number ,  "brand" :brand ,"model": model , "date" :date , "title" : title ,
                           "desc" : desc , "cause" : cause , "status" : 0 , "spec_id" : spec_id , "notified" : 0
                           })
        return redirect(url_for('pending_phone'))
        
    return render_template('add_phone.html')

@app.route('/pending_phone/' , methods = ["POST" , "GET"])
def pending_phone():
    pending = phones.find({"status" : 0})
    if request.method == 'POST':
        id = request.form['id']
        phones.find_one_and_update({"spec_id":id} ,{ '$set' :  {"status": 1}}) 
        
        return redirect(url_for('done_phones'))

    
    return render_template('pending_phone.html' , phones = pending)

@app.route('/done_phones' , methods =['POST','GET'])
def done_phones():
    done =  phones.find({"status" : 1})
    if request.method == 'POST':
        id = request.form['id']
        de_no = phones.find_one({'spec_id' : id})
        no = de_no['owner_number']
        #sms sending logic here.
        def send_sms(number):
            pass
        send_sms(no)
        phones.find_one_and_update({"spec_id":id} ,{ '$set' :  {"notified": 1}}) 

        return redirect(url_for('sent_notif'))
         
    return render_template('done_phones.html' ,  phone = done)

@app.route('/sent_notif/' , methods =['POST','GET'])
def sent_notif():
    session.pop('phone', None)
    sent = phones.find({"notified" : 1})
    if request.method == 'POST':
        id = request.form['id']
        session['phone'] = id
        return redirect(url_for('return_phone'))
    
    return render_template('sent_notif.html', phone = sent)


@app.route('/return_phone/' , methods=['POST','GET'])
def return_phone():
    ident = session['phone']
    the_phone = phones.find({"spec_id" : ident})

    
    return render_template('return_phone.html' , phone = the_phone , id = ident)



if __name__ == '__main__':
    app.secret_key = 'private_tings'
    app.run(debug=True,port=5008)