$password = "red9ranGe6"
$server = "root@65.109.207.182"

# اتصال به سرور و اجرای دستورات
$commands = @"
cd /root/py_bot
apt update
apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 init_db.py
"@

# ارسال دستورات به سرور
$commands | ssh $server 