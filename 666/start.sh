#!/bin/bash
# 激活虚拟环境
source venv/bin/activate

# 启动 Gunicorn
# Alwaysdata 会自动提供 $IP 和 $PORT 环境变量
exec gunicorn app:app --bind $IP:$PORT --workers 3
