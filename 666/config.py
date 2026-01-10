import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SETUP_CONFIG_PATH = BASE_DIR / 'setup.json'


def read_setup_config():
    try:
        with SETUP_CONFIG_PATH.open('r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_setup_config(data: dict):
    SETUP_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SETUP_CONFIG_PATH.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def update_setup_config(updates: dict):
    config = read_setup_config()
    config.update(updates)
    write_setup_config(config)
    return config


class Config:
    setup_data = read_setup_config()

    # 务必在生产环境中修改此密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or setup_data.get('secret_key') or 'dev-secret-key-change-me'
    
    # 数据库配置
    # 默认使用 SQLite (方便本地测试)，生产环境请设置环境变量 DATABASE_URL
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or setup_data.get('database_url') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SETUP_COMPLETED = bool(setup_data.get('setup_completed'))
