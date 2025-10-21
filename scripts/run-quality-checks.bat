@echo off
REM Run all quality checks locally before pushing (Windows version)
REM Usage: scripts\run-quality-checks.bat [backend|frontend|all]

setlocal enabledelayedexpansion

set TARGET=%1
if "%TARGET%"=="" set TARGET=all

echo ========================================
echo   RaptorFlow Quality Checks
echo ========================================
echo.

if "%TARGET%"=="backend" goto backend
if "%TARGET%"=="frontend" goto frontend
if "%TARGET%"=="all" goto all
echo Usage: %0 [backend^|frontend^|all]
exit /b 1

:backend
echo Running Backend Quality Checks...
cd backend

echo - Installing dependencies...
pip install -q -r requirements-dev.txt

echo - Running Ruff linter...
ruff check .
if errorlevel 1 (
    echo [ERROR] Ruff linting failed
    exit /b 1
)
echo [OK] Ruff linting passed

echo - Running Ruff formatter check...
ruff format --check .
if errorlevel 1 (
    echo [ERROR] Ruff formatting failed. Run 'ruff format .' to fix
    exit /b 1
)
echo [OK] Ruff formatting passed

echo - Running mypy type checking...
mypy . --config-file=../pyproject.toml
echo [OK] Type checking complete

echo - Running pytest...
pytest --cov=. --cov-report=term-missing
if errorlevel 1 (
    echo [ERROR] Tests failed
    exit /b 1
)
echo [OK] Tests passed

echo - Running security checks...
bandit -r . -f json -o bandit-report.json
echo [OK] Security scan complete

cd ..
echo [SUCCESS] Backend checks completed!
echo.

if "%TARGET%"=="backend" goto end
goto frontend_check

:frontend
:frontend_check
echo Running Frontend Quality Checks...
cd frontend

echo - Installing dependencies...
call npm install --silent

echo - Running TypeScript type checking...
call npm run type-check
if errorlevel 1 (
    echo [ERROR] Type checking failed
    exit /b 1
)
echo [OK] Type checking passed

echo - Running ESLint...
call npm run lint
if errorlevel 1 (
    echo [ERROR] Linting failed. Run 'npm run lint:fix' to auto-fix
    exit /b 1
)
echo [OK] Linting passed

echo - Running Prettier check...
call npm run format:check
if errorlevel 1 (
    echo [ERROR] Formatting failed. Run 'npm run format:write' to fix
    exit /b 1
)
echo [OK] Formatting passed

echo - Running unit tests...
call npm run test:coverage
if errorlevel 1 (
    echo [ERROR] Tests failed
    exit /b 1
)
echo [OK] Tests passed

cd ..
echo [SUCCESS] Frontend checks completed!
echo.

goto end

:all
call :backend
if errorlevel 1 exit /b 1
call :frontend_check
if errorlevel 1 exit /b 1

:end
echo ========================================
echo [SUCCESS] All quality checks passed!
echo ========================================
echo.
echo You're good to commit and push!
