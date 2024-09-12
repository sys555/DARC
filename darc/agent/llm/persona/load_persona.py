import json
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 定义数据库连接URL
db_url = 'postgresql+psycopg2://postgres:123456@localhost:5432/ain_repo'

# 创建数据库引擎
engine = create_engine(db_url, echo=True)

# 创建基类
Base = declarative_base()

# 定义Persona表
class Persona(Base):
    __tablename__ = 'persona'
    id = Column(Integer, primary_key=True, autoincrement=True)
    persona = Column(Text, nullable=False)

# 创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 读取 .jsonl 文件并插入数据
file_path = 'persona.jsonl'

with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        persona = Persona(persona=data['persona'])
        session.add(persona)

# 提交事务
session.commit()

print("Data inserted successfully.")