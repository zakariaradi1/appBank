from flask import Flask, request, render_template, session, url_for, redirect, Response, abort
from werkzeug.exceptions import HTTPException
import secrets
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from services import *

matplotlib.use('Agg')

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

adminService = AdminManage(cnx=DataBase.get_connection())
etlservice = Etl()
accserv = accmanger(cnx=DataBase.get_connection())

cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost.render.com:3306/db_Bank')
df = pd.read_sql('SELECT * FROM T_Accounts', con=cnx)

@app.errorhandler(HTTPException)
def handle_exception(e):
    return render_template('error.html', error=str(e.description)), e.code

@app.route("/dashboard1", methods=['GET'])
def dashboard1():
    try:
        results = adminService.count_Accounts_by_type()
        if not results:
            abort(404, description="No data available for account types")
        df = pd.DataFrame(results, columns=['Account_type', 'Account_count'])
        plt.figure()
        df.plot(kind='bar', x='Account_type', y='Account_count', legend=False, color='skyblue')
        plt.title("Nombre de comptes par type")
        plt.xlabel("Type de compte")
        plt.ylabel("Nombre de comptes")
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(img, content_type='image/png')
    except Exception as e:
        abort(500, description=str(e))

@app.route("/dashboard2", methods=['GET'])
def dashboard2():
    try:
        results = adminService.count_Accounts_by_year()
        if not results:
            abort(404, description="No data available for accounts by year")
        df = pd.DataFrame(results, columns=['creation_date', 'Accounts_count'])
        df['creation_date'] = pd.to_datetime(df['creation_date'])
        plt.figure(figsize=(10,6))
        plt.plot(df['creation_date'], df['Accounts_count'], marker='o', color='skyblue')
        plt.title("Nombre de comptes créés par date")
        plt.xlabel("Date de création")
        plt.ylabel("Nombre de comptes")
        plt.xticks(rotation=45, ha='right') 
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(img, content_type='image/png')
    except Exception as e:
        abort(500, description=str(e))

@app.route("/dashboard3", methods=['GET'])
def dashboard3():
    try:
        results = adminService.count_Accounts_by_balance()
        if not results:
            abort(404, description="No data available for accounts by balance")
        df = pd.DataFrame(results, columns=['Balance_Range', 'Account_count'])
        plt.figure()
        df.plot(kind='bar', x='Balance_Range', y='Account_count', legend=False, color='skyblue')
        plt.title("Nombre de comptes par tranche de solde")
        plt.xlabel("Tranche de solde")
        plt.ylabel("Nombre de comptes")
        plt.tight_layout()
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(img, content_type='image/png')
    except Exception as e:
        abort(500, description=str(e))

def initialize_database():
    try:
        print("Loading data from CSV into the database...")
        etlservice.load() 
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        abort(500, description="Error loading data into the database")

initialize_database()

def apply_monthly_updates_manually():
    try:
        accserv.apply_monthly_updates()
    except Exception as e:
        print(f"Error applying monthly updates: {str(e)}")
        abort(500, description="Error applying monthly updates")

apply_monthly_updates_manually()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/interfaceadministrative", methods=['GET', 'POST'])
def Acceuil():
    return render_template("interfaceadministrative.html")

@app.route("/withdraw", methods=['POST'])
def withdraw():
    try:
        email = request.form.get("email")
        amount = request.form.get("amount")
        if not email or not amount:
            return render_template("interfaceadministrative.html", error="Email and amount are required")
        withdraw = adminService.withdraw(email, amount) #type:ignore
        if withdraw:
            return render_template("interfaceadministrative.html", message="Withdraw done")
        else:
            return render_template("interfaceadministrative.html", error="Withdraw failed")
    except Exception as e:
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/deposit", methods=['POST'])
def deposit():
    try:
        email = request.form.get("email")
        amount = request.form.get("amount")
        if not email or not amount:
            return render_template("interfaceadministrative.html", error="Email and amount are required")
        deposit = adminService.deposit(email, amount) #type:ignore
        if deposit:
            return render_template("interfaceadministrative.html", message="Deposit done")
        else:
            return render_template("interfaceadministrative.html", error="Deposit failed")
    except Exception as e:
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/transferuser", methods=['POST'])
def transferuser():
    try:
        from_account = session.get('Email')
        to_account = request.form.get("to_account")
        amount = request.form.get("amount")
        if not from_account or not to_account or not amount:
            return render_template("interfaceuser.html", error="From account, to account, and amount are required")
        transfer = adminService.transfer(from_account, to_account, amount) #type:ignore
        if transfer:
            return render_template("interfaceuser.html", message="Transfer done")
        else:
            return render_template("interfaceuser.html", error="Transfer failed")
    except Exception as e:
        return render_template("interfaceuser.html", error=str(e))

@app.route("/transfer", methods=['POST'])
def transfer():
    try:
        from_account = request.form.get("from_account")
        to_account = request.form.get("to_account")
        amount = request.form.get("amount")
        if not from_account or not to_account or not amount:
            return render_template("interfaceadministrative.html", error="From account, to account, and amount are required")
        transfer = adminService.transfer(from_account, to_account, amount) #type:ignore
        if transfer:
            return render_template("interfaceadministrative.html", message="Transfer done")
        else:
            return render_template("interfaceadministrative.html", error="Transfer failed")
    except Exception as e:
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/create", methods=['POST'])
def create():
    try:
        Email = request.form.get("Email")
        balance = request.form.get("balance")
        Account_type = request.form.get("Account_type")
        password = request.form.get("password")
        if not Email or not balance or not Account_type or not password:
            return render_template("interfaceadministrative.html", error="All fields are required")
        create = adminService.insert_in_db(Email, balance, Account_type, password) #type:ignore
        if create:
            return render_template("interfaceadministrative.html", message="Account created")
        else:
            return render_template("interfaceadministrative.html", error="Account creation failed")
    except Exception as e:
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/delete", methods=['POST'])
def delete():
    try:
        email = request.form.get("email")
        if not email:
            return render_template("interfaceadministrative.html", error="Email is required")
        delete = adminService.delete(email)
        if delete:
            return render_template("interfaceadministrative.html", message="Account deletion success")
        else:
            return render_template("interfaceadministrative.html", error="Account deletion failed")
    except Exception as e:
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/deleteuser", methods=['POST'])
def deleteuser():
    try:
        email = session.get('Email')
        if not email:
            return render_template("interfaceuser.html", error="Email is required")
        delete = adminService.delete(email)
        if delete:
            return render_template("index.html", error="Deletion success")
        else:
            return render_template("interfaceuser.html", error="Account deletion failed")
    except Exception as e:
        return render_template("interfaceuser.html", error=str(e))

@app.route("/list", methods=['GET'])
def list():
    try:
        accounts = adminService.getAccounts()
        page = request.args.get('page', 1, type=int) 
        per_page = 4
        start = (page - 1) * per_page
        end = start + per_page
        paginated_accounts = accounts[start:end] 
        total_pages = (len(accounts) + per_page - 1) // per_page
        return render_template(
            "list.html",
            archived_accounts=paginated_accounts,
            page=page,
            total_pages=total_pages
        )
    except Exception as e:
        print("Error:", str(e)) 
        return render_template("interfaceadministrative.html", error=str(e))

@app.route("/auth", methods=['POST'])
def auth():
    try:
        login = request.form.get("Email")
        password = request.form.get("password")
        if not login or not password:
            return render_template('index.html', error="Email and password are required")
        account = adminService.auth(login, password) #type:ignore
        if account is None:
            return render_template('index.html', error="Login or password incorrect")
        session['Email'] = login
        return redirect(url_for('Acceuil'))
    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route("/interfacuser", methods=['GET', 'POST'])
def User():
    return render_template("interfaceuser.html")

@app.route("/loguser", methods=['POST'])
def loguser():
    try:
        login = request.form.get("Email")
        password = request.form.get("password")
        if not login or not password:
            return render_template('index.html', error="Email and password are required")
        account = adminService.loguser(login, password)
        if account is None:
            return render_template('index.html', error="Login or password incorrect")
        session['Email'] = login
        if account['Account_type'] == 'Admin':
            return redirect(url_for('Acceuil'))
        return redirect(url_for('User'))
    except Exception as e:
        return render_template('index.html', error=str(e))

from flask import request, render_template, redirect, url_for

@app.route('/Archivee', methods=['GET', 'POST'])
def Archivee():
    try:
        login = request.form.get("email") or request.args.get("email")
        if not login:
            return render_template("interfaceadministrative.html", error="Email is required")
        accounts = adminService.Archive(login)
        if not accounts:
            return render_template("interfaceadministrative.html", error="No archived accounts found")
        page = request.args.get('page', 1, type=int) 
        per_page = 3 
        start = (page - 1) * per_page
        end = start + per_page
        paginated_accounts = accounts[start:end] 
        total_pages = (len(accounts) + per_page - 1) // per_page

        return render_template(
            "archive.html",
            archived_accounts=paginated_accounts,
            email=login,
            page=page,
            total_pages=total_pages
        )
    except Exception as e:
        print("Error:", str(e)) 
        return render_template("interfaceadministrative.html", error=str(e))
    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
