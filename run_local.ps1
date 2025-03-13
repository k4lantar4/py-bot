# Function to check if a command was successful
function Test-LastExitCode {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Last command failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Stop and remove existing containers
Write-Host "Stopping and removing existing containers..." -ForegroundColor Yellow
docker-compose down
Test-LastExitCode

# Build and start containers
Write-Host "Building and starting containers..." -ForegroundColor Yellow
docker-compose build --no-cache
Test-LastExitCode
docker-compose up -d
Test-LastExitCode

# Wait for services to be ready
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py migrate
Test-LastExitCode

# Create superuser if it doesn't exist
Write-Host "Creating superuser if it doesn't exist..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"
Test-LastExitCode

# Import default messages
Write-Host "Importing default messages..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py import_default_messages --overwrite
Test-LastExitCode

# Create initial bot settings
Write-Host "Creating initial bot settings..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py shell -c "from telegram.models import BotSetting; BotSetting.objects.get_or_create(key='referral_bonus_amount', defaults={'value': '10000', 'description': 'Referral bonus amount in Toman', 'is_public': True})"
Test-LastExitCode

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Admin panel: http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host "API: http://localhost:8000/api" -ForegroundColor Cyan
Write-Host "Bot should be running and connected to Telegram" -ForegroundColor Cyan
Write-Host ""
Write-Host "Showing logs..." -ForegroundColor Yellow
docker-compose logs -f 