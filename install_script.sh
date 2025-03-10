#!/bin/bash

# نصب پیش‌نیازها
apt update
apt install -y python3-venv python3-pip

# ایجاد و فعال‌سازی محیط مجازی
cd /root/py_bot
python3 -m venv venv
source venv/bin/activate

# نصب نیازمندی‌ها
pip install -r requirements.txt

# راه‌اندازی پایگاه داده
python3 init_db.py 