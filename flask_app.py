from flask import Flask,render_template,request,redirect,Markup
#import oops_atm
import mysql.connector as con

flask_app=Flask(__name__,template_folder='templates')

pin_list=[]
balance=0
sl_no=0
user_pin=''
mydb = con.connect(host='localhost', user='root', password='mysqlp@$$')
mycursor=mydb.cursor()
mycursor.execute("create database if not exists atm")
mycursor.execute("use atm")
mycursor.execute("create table if not exists pin_records(sl_no int,atm_pin varchar(5))")

@flask_app.route("/",methods=["GET","POST"])
def home():
    try:
        if request.method=='GET':
             return render_template("index.html")
    except Exception as e:
        print(e)


@flask_app.route("/login",methods=['POST','GET'])
def login():
    pin_list=[]
    global user_pin
    try:
        if request.method=='POST':
           user_pin=request.form.get('user_pin')
           if user_pin=='':
               data_error=Markup("Kindly Enter ATM_PIN!")
               return render_template("index.html",login_error=data_error)
           print(user_pin)
           mycursor.execute("use atm")
           mycursor.execute("select distinct atm_pin from pin_records")
           pins = mycursor.fetchall()
           for i in pins:
               pin_list.append(i[0])
           for j in pin_list:
               print(j)
               if j==user_pin:
                    print(j,user_pin)
                    return render_template("credit_debit.html")
           else:
               error = Markup("ATM_PIN does not exist,kindly create")
               return render_template("index.html",error=error)
    except Exception as e:
        print(e)
    return render_template("index.html")

@flask_app.route("/register",methods=['POST','GET'])
def register():
    pin_list=[]
    global sl_no
    sl_no = sl_no + 1
    try:
        if request.method=='POST':
            user_pin=request.form.get("user_pin")
            mycursor.execute("use atm")
            mycursor.execute("select distinct atm_pin from pin_records")
            pins = mycursor.fetchall()
        else:
            if request.method=='GET':
                return render_template('register_pin.html')
    except Exception as e:
        print(e)
    else:
        for i in pins:
            pin_list.append(i[0])
        print(pin_list)
        for k in pin_list:
            if k == user_pin:
                return render_template("register_pin.html", error="pin taken,try again")
            elif len(user_pin) != 4:
                print("pin lengthy ,try again")
                return render_template("register_pin.html", error="PIN has to be equal to 4 digits only,try again")
        else:
            print("ATM_PIN created successfully")
            mycursor.execute("use atm")
            uploading = ("insert into pin_records(sl_no,atm_pin) values(%s,%s)")
            inserting = (sl_no, user_pin)
            mycursor.execute(uploading, inserting)
            mydb.commit()
            return redirect("/")


@flask_app.route("/credit",methods=['Post'])
def credit():
    try:
       global balance
       global deposit_amount
       deposit_amount = request.form.get("deposit_amt")
       if deposit_amount=='':
           data=Markup("Kindly Enter Amount!")
           return render_template("credit_debit.html",credit_error=data)
       print(deposit_amount)
       print("amount deposited",deposit_amount)
       balance=balance+int(deposit_amount)
       print(balance)
    except Exception as e:
        print(e)
    else:
       data=Markup("Amount Deposited is Rs:")+Markup(deposit_amount)+Markup("/-")
       return render_template("credit_debit.html", credit=data)

@flask_app.route("/debit", methods=['Post'])
def debit():
    try:
        global balance
        global withdraw_amount
        withdraw_amount = request.form.get("withdrawl_amt")
        if withdraw_amount=='':
            data=Markup("Kindly Enter Amount!")
            return render_template("credit_debit.html", debit_error=data)
        print(withdraw_amount)
        print("amount debited",withdraw_amount)
        balance=balance-int(withdraw_amount)
    except Exception as e:
        print(e)
    else:
       data=Markup("Amount Withdrawn is Rs:")+Markup(withdraw_amount)+Markup("/-")
       return render_template("credit_debit.html",debit=data)

@flask_app.route("/balance",methods=["GET"])
def check_balance():
    try:
        global balance
        global withdraw_amount
        global deposit_amount
        balance=int(deposit_amount)-int(withdraw_amount)
        print(balance)
    except Exception as e:
        print(e)
    else:
        data=Markup("Total balance is Rs:")+str(balance)+Markup("/-")
        return render_template("pin_balance.html",balance=data)

@flask_app.route("/pin",methods=['POST','GET'])
def change_pin():
    pin_list=[]
    try:
        global user_pin
        if request.method == 'POST':
            new_pin = request.form.get("new_pin")
            mycursor.execute("use atm")
            mycursor.execute("select distinct atm_pin from pin_records")
            pins = mycursor.fetchall()
        else:
            if request.method == 'GET':
                return render_template('pin_balance.html')
    except Exception as e:
        print(e)
    else:
        for i in pins:
            pin_list.append(i[0])
        for k in pin_list:
            if k == new_pin:
                return render_template("pin_balance.html", error="pin taken,try again")
            elif len(new_pin) != 4:
                print("pin lengthy ,try again")
                return render_template("pin_balance.html", error="PIN has to be equal to 4 digits only,try again")
            else:
                print("ATM_PIN changed successfully")
                mycursor.execute("use atm")
                update_sql = "update pin_records set atm_pin=%s where atm_pin=%s"
                update_value = new_pin, user_pin
                mycursor.execute(update_sql, update_value)
                mydb.commit()
                data = Markup("New ATM_PIN is :")+str(new_pin)
                return render_template("pin_balance.html", data=data)

@flask_app.route("/logout",methods=['GET'])
def logout():
    global balance
    global withdraw_amount
    global deposit_amount

    deposit_amount=0
    withdraw_amount=0
    balance=0
    return redirect("/")

if __name__=="__main__":
    flask_app.run(debug=True)