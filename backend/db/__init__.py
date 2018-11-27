import os
from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

def db_connect():
    if 'DB_USER_FA' in os.environ:
        DB_USER = os.environ['DB_USER_FA']
        DB_PASSWORD = os.environ['DB_PASSWORD_FA']
        DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
        DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
        return create_engine(DATABASEURI)
    else:
        raise Exception(
            'Database Credentials Not Found in the Environment Variables')
