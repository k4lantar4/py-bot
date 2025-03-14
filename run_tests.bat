@echo off
echo ===================================================
echo MRJBot Test Runner - Windows
echo ===================================================

echo Running simple component tests...
docker-compose -f docker-compose-simple-test.yml up --abort-on-container-exit
docker-compose -f docker-compose-simple-test.yml down

echo.
echo Running comprehensive tests...
docker-compose -f docker-compose-test-all.yml up --abort-on-container-exit
docker-compose -f docker-compose-test-all.yml down

echo.
echo Testing complete! Check the output above for results.
echo. 