from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

# 数据库配置
DATABASE_URL = 'postgresql://postgres:123456@localhost:5432/ain_repo'

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# 定义User模型
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    inserted_at = Column(DateTime, nullable=False)

# 创建表（如果表不存在）
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 插入数据函数
def insert_user(username, email, naive_dt):
    # 将naive datetime转换为aware datetime
    aware_dt = naive_dt.replace(tzinfo=timezone.utc)

    new_user = User(username=username, email=email, inserted_at=aware_dt)
    session.add(new_user)
    session.commit()

# 示例数据
username = 'testuser2'
email = 'testuser@example.comm'
naive_dt = datetime(2024, 8, 2, 5, 42, 34)

# 调用插入数据函数
insert_user(username, email, naive_dt)

# 关闭会话
session.close()