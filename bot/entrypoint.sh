#!/bin/bash

# اجرای مهاجرت‌های پایگاه داده در صورت نیاز
echo "Waiting for database to be ready..."
python wait_for_db.py

# اجرای دستور نهایی
exec "$@" 