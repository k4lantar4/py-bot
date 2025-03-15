#!/bin/bash
set -e

echo "🚀 Starting MRJBot Telegram Bot..."

# بررسی محیط و پایگاه داده
echo "🔍 Checking environment..."
python -c "import os; print(f'Working directory: {os.getcwd()}')"
python -c "import sys; print(f'Python path: {sys.path}')"

# صبر برای آماده شدن پایگاه داده
echo "⏳ Waiting for database to be ready..."
if [ -f "/app/wait_for_db.py" ]; then
    python /app/wait_for_db.py
else
    echo "❌ Warning: wait_for_db.py not found!"
    # انتظار ساده برای پایگاه داده
    sleep 5
fi

echo "✅ Entrypoint completed successfully!"
echo "🤖 Running command: $@"

# اجرای دستور نهایی
exec "$@" 