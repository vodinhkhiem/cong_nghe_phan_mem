from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from config import Config
from infrastructure.databases.base import Base

# 1. Khởi tạo Engine
DATABASE_URI = Config.DATABASE_URI
engine = create_engine(
    DATABASE_URI, 
    pool_size=10, 
    max_overflow=20, 
    pool_pre_ping=True
)

# 2. Tạo Scoped Session
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Biến session này có thể dùng trực tiếp hoặc qua SessionLocal()
session = SessionLocal

def init_mssql(app):
    """Khởi tạo bảng và thiết lập dọn dẹp session tự động"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ MSSQL Initialized successfully and tables created.")
    except Exception as e:
        print(f"❌ Failed to initialize MSSQL: {e}")
        raise e
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()