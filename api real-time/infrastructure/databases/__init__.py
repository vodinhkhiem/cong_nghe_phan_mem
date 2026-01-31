from infrastructure.databases.mssql import init_mssql
from infrastructure.databases.base import Base
from infrastructure.databases.mssql import engine

def init_db(app):
    init_mssql(app)
    
from infrastructure.databases.mssql import Base
