from dataclasses import dataclass
from datetime import datetime



@dataclass
class Account:
    Email:str
    Account_id:int
    balance:float
    Account_type:str
    created_at:datetime
    password:str
    interestRate:float
    transaction_count:int
    last_transaction_reset:datetime

    

@dataclass
class Archive:
    id:int
    Email:str
    Balance:float
    Operation:str   
    Operation_time:datetime


@dataclass 
class Location:
    email:str
    ip_address:str
    location:str
    count:int