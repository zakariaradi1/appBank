from flask import Blueprint, Flask, request, render_template, session, url_for, redirect,send_file
from services.user_service import UserManage
from errors.error_handler import handle_exception
from dal.user_dal import DataBase

user_bp = Blueprint('user_bp', __name__)

userService = UserManage(cnx=DataBase.get_connection())

@user_bp.errorhandler(Exception) # type: ignore
def user_error_handler(e):
    return handle_exception(e)


@user_bp.route("/")
def index():
    return render_template("index.html")



@user_bp.route("/interfacuser", methods=['GET', 'POST'])
def User():
    login = session.get('Email')
    if not login:
        return redirect(url_for('index'))
    otp = userService.generate_otp(login)
    return render_template("interfaceuser.html",otp=otp)


@user_bp.route("/loguser", methods=['POST'])
def loguser():
    try:
        login = request.form.get("Email")
        password = request.form.get("password")
        if not login or not password:
            return render_template('index.html', error="Email and password are required")
        account = userService.loguser(login, password)
        if account is None:
            return render_template('index.html', error="Login or password incorrect")
        session['Email'] = login
        session['Account_type'] = account['Account_type']
        if userService.is_first_login(login):
            userService.addip(login)
            if account['Account_type'] == 'Admin':
                return redirect(url_for('Acceuil', message="First login successful!"))
            else:
                return redirect(url_for('User', message="First login successful!"))
        if not userService.authip(login):
            return redirect(url_for('otp_verification'))
        if account['Account_type'] == 'Admin':
            return redirect(url_for('Acceuil', message="Login successful!"))
        else:
            return redirect(url_for('User', message="Login successful!"))
    
    except Exception as e:
        return render_template('index.html', error=str(e))


@user_bp.route("/logout",methods=['POST'])   
def logout():
    session.clear()
    return redirect(url_for('index'))


@user_bp.route("/deleteuser", methods=['POST'])
def deleteuser():
    try:
        email = session.get('Email')
        if not email:
            return render_template("interfaceuser.html", error="Email is required")
        delete = userService.delete(email)
        if delete:
            return render_template("index.html", error="Deletion success")
        else:
            return render_template("interfaceuser.html", error="Account deletion failed")
    except Exception as e:
        return render_template("interfaceuser.html", error=str(e))
    
    

@user_bp.route("/transferuser", methods=['POST'])
def transferuser():
    try:
        from_account = session.get('Email')
        to_account = request.form.get("to_account")
        amount = request.form.get("amount")
        if not from_account or not to_account or not amount:
            return render_template("interfaceuser.html", error="From account, to account, and amount are required")
        transfer = userService.transfer(from_account, to_account, amount) #type:ignore
        if transfer:
            return render_template("interfaceuser.html", message="Transfer done")
        else:
            return render_template("interfaceuser.html", error="Transfer failed")
    except Exception as e:
        return render_template("interfaceuser.html", error=str(e))
    
    

@user_bp.route("/otp_verification", methods=['GET', 'POST'])
def otp_verification():
    return render_template('otp_verification.html')


@user_bp.route("/verify_otp", methods=['POST'])
def verify_otp():
    login = session.get('Email')
    if not login:
        return redirect(url_for('index'))
    otp = request.form.get("otp")
    if userService.verify_otp(login, otp): #type:ignore
        userService.approve_login(login)
        userService.addip(login) #type:ignore
        account_type = session.get('Account_type')
        if account_type == 'Admin':
            return redirect(url_for('Acceuil'))
        else:
            return redirect(url_for('User'))
    else:
        return render_template('otp_verification.html', error="Invalid or expired OTP")
    
@user_bp.route('/delete-otp', methods=['POST'])
def delete_otp():
    session.pop('otp', None)
    return redirect(url_for('interfaceadministrative.html', message="success"))



@user_bp.route("/verify_ip", methods=['GET', 'POST'])
def verify_ip():
    login = session.get('Email')
    if not login:
        return render_template('verify_ip.html', error="No login session found")
    if request.method == 'POST':
        userService.approve_login(login)
        account_type = session.get('Account_type')
        if account_type == 'Admin':
            return redirect(url_for('Acceuil', message="IP verification successful!"))
        else:
            return redirect(url_for('User', message="IP verification successful!"))
    return render_template('verify_ip.html')


@user_bp.route("/check_approval")
def check_approval():
    login = session.get('Email')
    if login:
        status = userService.get_latest_login_attempt(login)
        if status == "approved":
            account_type = session.get('Account_type')
            if account_type == 'Admin':
                return redirect(url_for('Acceuil',message="approved"))
            return redirect(url_for('User',message="approved"))
        return redirect(url_for('index',message="declined"))
    return redirect(url_for('index'))

@user_bp.route("/approve_login")
def approve_login():
    login = session.get('Email')
    if login:
        userService.approve_login(login)
        return "Login approved! You can now return to the login page."
    return "No login session found."


@user_bp.route("/decline_login")
def decline_login():
    login = session.get('Email')
    if login:
        userService.decline_login(login)
        session.clear()
        return redirect(url_for('index', message="Login declined!"))
    return redirect(url_for('Acceuil', message="No login session found."))



@user_bp.route("/change_password", methods=["POST"])
def change_password():
    email = session.get('Email')
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")
    if not userService.is_password_valid(email,new_password): #type:ignore
        return redirect(url_for('User', error='password must be at least 8 characters and uppercase and lowercase letters and numbers'))
    if new_password != confirm_password:
        return redirect(url_for('User', error='password not changed the confirme password is not the same'))
    return redirect(url_for('User', message='password changed successfuly'))


@user_bp.route('/generate_pdf', methods=['GET','POST'])
def generate_pdf():
    email = session.get('Email')
    download = request.args.get('download')

    archives = adminService.Archive(email) # type: ignore
    print(f"Archives trouvées : {archives}") 
    pdf_buffer = PDFGenerator.generate_pdf(archives, email) # type: ignore
    if download:
        return send_file(pdf_buffer, as_attachment=True, download_name="report.pdf")
    return send_file(pdf_buffer, mimetype='application/pdf') 


