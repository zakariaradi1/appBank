from flask import Blueprint, Flask, request, render_template, session, url_for, redirect, Response, abort,send_file
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
from services.admin_service import AdminManage,accmanager
from errors.error_handler import *
from dal.admin_dal import DataBase

matplotlib.use('Agg')

admin_bp = Blueprint('admin_bp', __name__)

adminService = AdminManage(cnx=DataBase.get_connection())
accserv = accmanager(cnx=DataBase.get_connection())

@admin_bp.errorhandler(Exception) # type: ignore
def admin_error_handler(e):
    return handle_exception(e)

@admin_bp.route("/dashboard1", methods=['GET'])
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

@admin_bp.route("/dashboard2", methods=['GET'])
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

@admin_bp.route("/dashboard3", methods=['GET'])
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


@admin_bp.route("/")
def index():
    return render_template("index.html")


@admin_bp.route("/interfaceadministrative", methods=['GET', 'POST'])
def Acceuil():
    login = session.get('Email')
    if not login:
        return redirect(url_for('index'))
    otp = adminService.generate_otp(login)
    return render_template('interfaceadministrative.html', otp=otp)


@admin_bp.route("/loguser", methods=['POST'])
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
        session['Account_type'] = account['Account_type']
        if adminService.is_first_login(login):
            adminService.addip(login)
            if account['Account_type'] == 'Admin':
                return redirect(url_for('Acceuil', message="First login successful!"))
            else:
                return redirect(url_for('User', message="First login successful!"))
        if not adminService.authip(login):
            return redirect(url_for('otp_verification'))
        if account['Account_type'] == 'Admin':
            return redirect(url_for('Acceuil', message="Login successful!"))
        else:
            return redirect(url_for('User', message="Login successful!"))
    
    except Exception as e:
        return render_template('index.html', error=str(e))


@admin_bp.route("/logout",methods=['POST'])   
def logout():
    session.clear()
    return redirect(url_for('index'))


@admin_bp.route("/create", methods=['POST'])
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


@admin_bp.route("/delete", methods=['POST'])
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
    

@admin_bp.route("/list", methods=['GET'])
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


@admin_bp.route("/deposit", methods=['POST'])
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
    
    
@admin_bp.route("/withdraw", methods=['POST'])
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
    
    
@admin_bp.route("/transfer", methods=['POST'])
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
    
    
@admin_bp.route("/otp_verification", methods=['GET', 'POST'])
def otp_verification():
    return render_template('otp_verification.html')


@admin_bp.route("/verify_otp", methods=['POST'])
def verify_otp():
    login = session.get('Email')
    if not login:
        return redirect(url_for('index'))
    otp = request.form.get("otp")
    if adminService.verify_otp(login, otp): #type:ignore
        adminService.approve_login(login)
        adminService.addip(login) #type:ignore
        account_type = session.get('Account_type')
        if account_type == 'Admin':
            return redirect(url_for('Acceuil'))
        else:
            return redirect(url_for('User'))
    else:
        return render_template('otp_verification.html', error="Invalid or expired OTP")
    
@admin_bp.route('/delete-otp', methods=['POST'])
def delete_otp():
    session.pop('otp', None)
    return redirect(url_for('interfaceadministrative.html', message="success"))



@admin_bp.route("/verify_ip", methods=['GET', 'POST'])
def verify_ip():
    login = session.get('Email')
    if not login:
        return render_template('verify_ip.html', error="No login session found")
    if request.method == 'POST':
        adminService.approve_login(login)
        account_type = session.get('Account_type')
        if account_type == 'Admin':
            return redirect(url_for('Acceuil', message="IP verification successful!"))
        else:
            return redirect(url_for('User', message="IP verification successful!"))
    return render_template('verify_ip.html')


@admin_bp.route("/check_approval")
def check_approval():
    login = session.get('Email')
    if login:
        status = adminService.get_latest_login_attempt(login)
        if status == "approved":
            account_type = session.get('Account_type')
            if account_type == 'Admin':
                return redirect(url_for('Acceuil',message="approved"))
            return redirect(url_for('User',message="approved"))
        return redirect(url_for('index',message="declined"))
    return redirect(url_for('index'))

@admin_bp.route("/approve_login")
def approve_login():
    login = session.get('Email')
    if login:
        adminService.approve_login(login)
        return "Login approved! You can now return to the login page."
    return "No login session found."


@admin_bp.route("/decline_login")
def decline_login():
    login = session.get('Email')
    if login:
        adminService.decline_login(login)
        session.clear()
        return redirect(url_for('index', message="Login declined!"))
    return redirect(url_for('Acceuil', message="No login session found."))


@admin_bp.route('/Archivee', methods=['GET', 'POST'])
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
            total_pages=total_pages,
            archives=accounts
        )
    except Exception as e:
        print("Error:", str(e)) 
        return render_template("interfaceadministrative.html", error=str(e))
    
    
    
@admin_bp.route('/generate_pdfadm', methods=['GET','POST'])
def generate_pdfadm():
    email = request.form.get('email')
    download = request.form.get('download')

    archives = adminService.Archive(email) # type: ignore
    print(f"Archives trouvées : {archives}") 
    pdf_buffer = PDFGenerator.generate_pdf(archives, email) # type: ignore

    if download:
        return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf")
    return send_file(pdf_buffer, mimetype='application/pdf') 

    
