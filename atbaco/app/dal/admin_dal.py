from io import BytesIO
import mysql.connector as my
from sqlalchemy import create_engine
import pandas as ps
from models.models import *
from datetime import datetime, timedelta
from flask import request
from fpdf import FPDF
import requests
import random

class DataBase:
    cnx = None

    @staticmethod
    def get_connection():
        if DataBase.cnx is None:
            try:
                DataBase.cnx = my.connect(
                    user="root",
                    password="zakaria1234radi@",
                    host="localhost",
                    database="db_Bank"
                )
                print('Connection OK')
            except Exception as e:
                print(f'Connection Error: {e}')
                return None
        return DataBase.cnx

IPINFO_TOKEN = 'f8099caac4fc4b'
class AdminDao:
    def __init__(self, cnx):
        self.cnx = cnx
        self.account_manager = AccountManager(cnx)




    def loguser(self, email: str, password: str) -> dict | None:
        Account_id = email
        query = "SELECT Account_type FROM T_Accounts WHERE Email=%s OR Account_id = %s AND password=%s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,Account_id,password))
            row = cursor.fetchone()
            if row is not None:
                return row
            return None
        return None



    def log_user_location(self, email: str, ip_address: str, location: str) -> bool:
        try:
            check_query = "SELECT count FROM T_Locations WHERE email=%s AND ip_address=%s;"
            insert_query = "INSERT INTO T_Locations (email, ip_address, location, count) VALUES (%s, %s, %s, %s);"
            update_query = "UPDATE T_Locations SET count = count + 1 WHERE email=%s AND ip_address=%s;"
            if self.cnx is not None:
                cursor = self.cnx.cursor(dictionary=True)
                cursor.execute(check_query, (email, ip_address))
                row = cursor.fetchone()
                if row:
                    cursor.execute(update_query, (email, ip_address))
                else:
                    cursor.execute(insert_query, (email, ip_address, location, 1))
                self.cnx.commit()
                cursor.close()
                return True
        except Exception as e:
            return False
        return False



    
    def delete(self, email: str) -> bool:
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            query = "SELECT Account_id, balance FROM T_Accounts WHERE Email = %s;"
            cursor.execute(query, (email,))
            account_data = cursor.fetchone()
            if account_data:
                balance = account_data['balance']
                if balance < 0:
                    return False 
                if balance > 0:
                    principal_account_mail = "principale@gmail.com"
                    self.transfer(email,principal_account_mail,balance)
                    self.account_manager.archive_transaction(email, balance, "Deletion")
                delete_query = "DELETE FROM T_Accounts WHERE Email = %s;"
                cursor.execute(delete_query, (email,))
                self.cnx.commit()
                return True
        
        return False
    


    def getAccounts(self)->list[Account]:
        users:list[Account]=[]
        query:str = "SELECT * FROM T_Accounts"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows :
                users.append(Account(**row)) # type: ignore
            return users 
        return []
      
      
      
    def getAccountsbyemail(self,email:str):
        query:str = "SELECT email FROM T_Accounts where Email = %s"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query,(email,))
            row = cursor.fetchone()
            if row != None:
                return row 
            return None   



    def deposit(self, email: str, amount: float) -> bool:
        query = """
            UPDATE T_Accounts 
            SET balance = balance + %s, transaction_count = transaction_count + 1 
            WHERE email = %s;
        """
        self.account_manager.archive_transaction(email, amount, "deposit")
        if self.cnx is not None:
            cursor = self.cnx.cursor()
            cursor.execute(query, (amount, email))
            self.cnx.commit()
            self.account_manager.apply_monthly_updates()
            
            return True
        return False

    def withdraw(self, email: str, amount: float) -> bool:
        query = "SELECT Account_type, balance FROM T_Accounts WHERE Email = %s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            account = cursor.fetchone()

            if account:
                account_type = account["Account_type"]
                balance = float(account["balance"])
                amount = float(amount)  

                if account_type == "saving" and (balance - amount) < 100:
                    print("Erreur : Le solde du compte saving ne peut pas être inférieur à 100 après un retrait.")
                    return False
                elif account_type == "checking" and (balance - amount) < 0:
                    print("Erreur : Solde insuffisant pour effectuer le retrait.")
                    return False

                update_query = """
                    UPDATE T_Accounts 
                    SET balance = balance - %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                cursor.execute(update_query, (amount, email))
                self.cnx.commit()
                self.account_manager.archive_transaction(email, amount, "withdraw")
                self.account_manager.apply_monthly_updates()
                return True
            else:
                return False
        return False

    def transfer(self, email: str, email2: str, amount: float) -> bool:
        query = "SELECT Account_type, balance FROM T_Accounts WHERE Email = %s;"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            source_account = cursor.fetchone()
            if source_account:
                source_account_type = source_account["Account_type"]
                source_balance = float(source_account["balance"])  
                amount = float(amount)  
                if source_account_type == "saving" and (source_balance - amount) < 100:
                    return False
                elif source_balance < amount:
                    return False
                update_query_source = """
                    UPDATE T_Accounts 
                    SET balance = balance - %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                update_query_destination = """
                    UPDATE T_Accounts 
                    SET balance = balance + %s, transaction_count = transaction_count + 1 
                    WHERE email = %s;
                """
                cursor.execute(update_query_source, (amount, email))
                cursor.execute(update_query_destination, (amount, email2))
                self.cnx.commit()
                self.account_manager.archive_transaction(email, amount, "transfer_out to " + email2)
                self.account_manager.archive_transaction(email2, amount, "transfer_in from " + email)
                self.account_manager.apply_monthly_updates()
                return True
            else:
                return False
        return False


    def Archive(self, email: int | str) -> list[Archive]:
        Archives: list[Archive] = []
        query = "SELECT Email FROM T_Accounts WHERE Account_id = %s;"
        query1 = "SELECT * FROM T_Archive WHERE Email = %s"
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            if isinstance(email, int):
                cursor.execute(query, (email,))
                row = cursor.fetchone()
                if row is None:
                    return []
                email = row["Email"] 
            cursor.execute(query1, (email,))
            rows = cursor.fetchall()
            for row in rows:
                Archives.append(Archive(**row))  # type: ignore
            
        return Archives

                    
    def insert_in_db(self, email: str, balance: float, Account_type: str, password: str, interest: float = 0, transaccoun: int = 0, last: datetime = datetime.now()) -> bool:
        cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost/db_Bank')
        data = {
            "Email": [email],
            "Balance": [balance],
            "Account_type": [Account_type],
            "password": [password],
            "interestRate": [interest],
            "transaction_count": [transaccoun],
            "last_transaction_reset": [last]
        }
        df = ps.DataFrame(data)
        df.to_sql(name='T_Accounts', con=cnx, if_exists='append', index=False)
        self.account_manager.archive_transaction(email, balance, "creation")
        if self.cnx is not None:
            self.cnx.commit()
            return True
        return False




    def addip(self, email: str) -> bool:
        if self.cnx is not None:
            try:
                ip_address = request.remote_addr
                response = requests.get(f'https://ipinfo.io/{ip_address}/json?token={IPINFO_TOKEN}')
                location_data = response.json()
                city = location_data.get('city')
                country = location_data.get('country')
                location = f"{city}, {country}" if city and country else "Unknown"
                return self.log_user_location(email, ip_address, location)  # type: ignore
            except Exception as e:
                print(f"Error fetching location or logging IP: {e}")
                return False
        return False
    
    
    
    def authip(self, email: str) -> bool:
        if self.cnx is None:
            print("Database connection is not available.")
            return False
        
        try:
            query = "SELECT COUNT(*) AS count FROM T_Locations WHERE email = %s;"
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            cursor.close()
            
            if row and row["count"] == 0:
                return True
            ip_query = "SELECT ip_address FROM T_Locations WHERE email = %s;"
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(ip_query, (email,))
            ip_rows = cursor.fetchall()
            cursor.close()
            
            current_ip = request.remote_addr
            for ip_row in ip_rows:
                if ip_row["ip_address"] == current_ip:
                    print("IP is recognized.")
                    return True  
            return False 
        except Exception as e:
            return False
    

    def is_first_login(self, email: str) -> bool:
        login_attempt_query = "SELECT COUNT(*) AS count FROM T_LoginAttempts WHERE Email = %s;"
        location_query = "SELECT COUNT(*) AS count FROM T_Locations WHERE email = %s;"
        if self.cnx:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(login_attempt_query, (email,))
            login_attempt_row = cursor.fetchone()
            cursor.execute(location_query, (email,))
            location_row = cursor.fetchone()
            cursor.close()
            if login_attempt_row and location_row and login_attempt_row["count"] == 0 and location_row["count"] == 0:
                return True
        return False
    

    def create_login_attempt(self, email: str) -> bool:
        query = "INSERT INTO T_LoginAttempts (Email, status) VALUES (%s, 'pending');"
        if self.cnx:
            cursor = self.cnx.cursor()
            cursor.execute(query, (email,))
            self.cnx.commit()
            cursor.close()
            return True
        return False

    def get_latest_login_attempt(self, email: str) -> dict | None:
        query = "SELECT status, otp FROM T_LoginAttempts WHERE Email=%s ORDER BY timestamp DESC LIMIT 1;"
        if self.cnx:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            cursor.close()
            return row
        return None

    

    def generate_otp(self, email: str) -> str | None:
        otp = str(random.randint(100000, 999999))

        query = """
        INSERT INTO T_LoginAttempts (Email, otp, status,otp_expires_at)
        VALUES (%s, %s, 'pending',NOW() + INTERVAL 5 MINUTE)
        ON DUPLICATE KEY UPDATE otp=%s, otp_expires_at=NOW() + INTERVAL 5 MINUTE;
        """

        if self.cnx:
            cursor = self.cnx.cursor()
            cursor.execute(query, (email, otp, otp))
            self.cnx.commit()
            cursor.close()
            return otp
        return None


    def verify_otp(self, email: str, otp: str) -> bool:
        query = "SELECT otp FROM T_LoginAttempts WHERE Email=%s ;"
        if self.cnx:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            cursor.close()
            if row and row["otp"] == otp:
                return True
        return False


    def get_otp(self, email: str) -> str | None:
        query = "SELECT otp FROM T_LoginAttempts WHERE Email=%s ORDER BY timestamp DESC LIMIT 1;"
        if self.cnx:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            cursor.close()
            return row["otp"] if row and row["otp"] else None
        return None
    
    
    
    def approve_login(self, email: str) -> bool:
        query = "UPDATE T_LoginAttempts SET status='approved' WHERE Email=%s;"
        if self.cnx:
            cursor = self.cnx.cursor()
            cursor.execute(query, (email,))
            self.cnx.commit()
            cursor.close()
            return True
        return False

    def decline_login(self, email: str) -> bool:
        query = "UPDATE T_LoginAttempts SET status='declined' WHERE Email=%s;"
        if self.cnx:
            cursor = self.cnx.cursor()
            cursor.execute(query, (email,))
            self.cnx.commit()
            cursor.close()
            return True
        return False
    
    
    
    
    
    def is_password_valid(self,email:str,password:str):
        
        if len(password) < 8:
            return False
        has_upper = any(char.isupper() for char in password)
        if not has_upper:
            return False
        has_lower = any(char.islower() for char in password)
        if not has_lower:
            return False
        has_digit = any(char.isdigit() for char in password)
        if not has_digit:
            return False
        has_symbol = any(not char.isalnum() for char in password)
        if not has_symbol:
            return False
        query:str = "UPDATE T_Accounts set password = %s where Email = %s"
        if self.cnx != None:
            cursor = self.cnx.cursor(dictionary=True)
            cursor.execute(query,(password,email))
            rows = cursor.fetchone()
            if rows is not None:
                return True
            return True
        
    


    def count_Accounts_by_type(self):
        if self.cnx is not None:
            db = self.cnx.cursor()
            db.execute("""
                SELECT Account_type, COUNT(*) AS Account_count
                FROM T_Accounts
                GROUP BY Account_type;
            """)
            results = db.fetchall()
            return results
        else:
            print("Connection not available")
            return None



    def count_Accounts_by_year(self):
        if self.cnx is not None:
            db = self.cnx.cursor()
            query = """
                SELECT DATE(created_at) AS creation_date, COUNT(*) AS Accounts_count
                FROM T_Accounts
                GROUP BY creation_date
                ORDER BY creation_date;
            """
            db.execute(query)
            results = db.fetchall()
            return results
        else:
            print("Connection not available")
            return None



    def count_Accounts_by_balance(self):
        if self.cnx is not None:
            db = self.cnx.cursor()
            query = """
                SELECT
                    CASE
                        WHEN balance <= 10000 THEN 'Below 10,000'
                        WHEN balance > 10000 AND balance <= 100000 THEN 'Between 10,000 and 100,000'
                        ELSE 'Above 100,000'
                    END AS Balance_Range,
                    COUNT(*) AS Account_count
                FROM T_Accounts
                GROUP BY Balance_Range;
            """
            db.execute(query)
            results = db.fetchall()
            return results
        else:
            print("Connection not available")
            return None
        
        
    
    def generate_pdf(self,archives, email: str) -> BytesIO:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Archive Report for {email}", ln=True, align="C") # type: ignore
        pdf.ln(10)
        if not archives:
            pdf.set_font("Arial", size=10, style="B")
            pdf.cell(200, 10, "No records found.", ln=True, align="C")
        else:
            pdf.set_font("Arial", size=10, style="B")
            pdf.cell(40, 10, "Archive ID", border=1)
            pdf.cell(60, 10, "Email", border=1)
            pdf.cell(40, 10, "Action", border=1)
            pdf.cell(40, 10, "Timestamp", border=1)
            pdf.ln()
            pdf.set_font("Arial", size=10)
            for archive in archives:
                archive_id = str(getattr(archive, "id", "N/A"))
                email = getattr(archive, "Email", "N/A")
                action = getattr(archive, "Operation", "N/A")
                timestamp = getattr(archive, "Operation_time", "N/A")
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                pdf.cell(40, 10, archive_id, border=1)
                pdf.cell(60, 10, email, border=1)
                pdf.cell(40, 10, action, border=1)
                pdf.cell(40, 10, str(timestamp), border=1)
                pdf.ln()
                
        pdf_buffer = BytesIO()
        pdf_buffer.write(pdf.output(dest="S").encode("latin1")) # type: ignore
        pdf_buffer.seek(0)
        
        return pdf_buffer

        

class AccountManager:
    FREE_TRANSACTIONS = 5 
    TRANSACTION_FEE = 1.0 
    MINIMUM_BALANCE = 100.0 

    def __init__(self, cnx):
        self.cnx = cnx
    
    def apply_monthly_updates(self):
        if self.cnx is not None:
            cursor = self.cnx.cursor(dictionary=True)
            query = """
                SELECT Email, balance, Account_type, interestRate, transaction_count, created_at, last_transaction_reset
                FROM T_Accounts;
            """
            cursor.execute(query)
            accounts = cursor.fetchall()

            for account in accounts:
                email = account["Email"]
                balance = account["balance"]
                account_type = account["Account_type"]
                interest_rate = account.get("interestRate", 0.0)
                transaction_count = account.get("transaction_count", 0)
                created_at = account["created_at"]
                last_transaction_reset = account.get("last_transaction_reset")

                current_date = datetime.now().date()

                if account_type == "saving":
                    account_age = (current_date - created_at.date()).days // 365
                    if account_age > 0 and (last_transaction_reset is None or (current_date - last_transaction_reset).days >= 365):
                        interest = balance * interest_rate
                        balance += interest
                        self.archive_transaction(email, interest, "annual_interest")
                        update_query = """
                            UPDATE T_Accounts
                            SET balance = %s, last_transaction_reset = %s
                            WHERE Email = %s;
                        """
                        cursor.execute(update_query, (balance, current_date, email))
                        self.cnx.commit()

                elif account_type == "checking":
                    if last_transaction_reset is None or (current_date - last_transaction_reset).days >= 30:
                        if transaction_count > AccountManager.FREE_TRANSACTIONS:
                            excess = transaction_count - AccountManager.FREE_TRANSACTIONS
                            fees = excess * AccountManager.TRANSACTION_FEE
                            balance -= fees
                            self.archive_transaction(email, fees, "transaction_fees")
                        transaction_count = 0
                        last_transaction_reset = current_date

                        update_query = """
                            UPDATE T_Accounts
                            SET balance = %s, transaction_count = %s, last_transaction_reset = %s
                            WHERE Email = %s;
                        """
                        cursor.execute(update_query, (balance, transaction_count, last_transaction_reset, email))
                        self.cnx.commit()



    def archive_transaction(self, email: str, amount: float, operation: str):
        cnx = create_engine('mysql+mysqlconnector://root:zakaria1234radi%40@localhost/db_Bank')
        data = {
            "Email": [email],
            "Balance": [amount],
            "Operation": [operation]
        }
        df = ps.DataFrame(data)
        df.to_sql(name='T_Archive', con=cnx, if_exists='append', index=False)
