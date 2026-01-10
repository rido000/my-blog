import os

class Config:
    # 务必在生产环境中修改此密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me'
    
    # 数据库配置
    # 默认使用 SQLite (方便本地测试)，生产环境请设置环境变量 DATABASE_URL
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
