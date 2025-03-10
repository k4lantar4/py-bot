# Installation Issues Fixes

This document outlines the fixes applied to the installation script to resolve various issues.

## 1. PHP JSON Extension

**Issue:** Failed to install `php8.2-json` because it doesn't exist as a separate package in PHP 8.2+.

**Fix:** Removed `php8.2-json` from the prerequisites list since the JSON extension is now bundled with the core PHP package.

## 2. Apache Service Issues

**Issue:** Apache service failed to restart, with error code when running `systemctl restart apache2`.

**Fix:** 
- Added better error handling and diagnostics for Apache service restart
- Added configtest to identify configuration errors
- Added automatic enabling of required modules (rewrite, ssl)
- Added detailed error messages with references to log files
- Properly configured phpMyAdmin to work with Apache

## 3. MySQL Access and Security Issues

**Issue:** Multiple errors related to MySQL root access being denied and secure installation failing.

**Fix:**
- Improved password handling with confirmation
- Added detection of passwordless root access (common in fresh installations)
- Created proper SQL script to securely configure MySQL
- Used direct SQL execution rather than shell scripts for better security
- Improved error handling with detailed messages
- Added validation of MySQL connection after setup

## 4. Backend Dependencies Installation Issues

**Issue:** Failed to build wheels for Python packages like aiohttp and pendulum, with errors related to missing build tools and Python 3.12 compatibility issues.

**Fix:**
- Added installation of build dependencies (setuptools, wheel) before installing backend requirements
- Added special handling for Python 3.12 to install distutils
- Added option to install packages one by one if batch installation fails
- Used `--no-build-isolation` flag to improve build reliability
- Added better error reporting and graceful continuation options

## How These Fixes Work

1. **PHP JSON Extension** - Simply removed the unnecessary package from the installation list.

2. **Apache Service** - Added multiple layers of diagnostics and auto-correction to identify and fix common Apache configuration issues.

3. **MySQL Security** - Completely rewrote the MySQL security setup to be more robust, using proper SQL execution instead of shell scripts.

4. **Backend Dependencies** - Added proper building tools installation and fallback mechanisms to handle Python 3.12 compatibility issues.

## Additional Notes

- The installation script now has better error handling and diagnostic messages
- It attempts to continue installation even if some non-critical steps fail
- It provides specific guidance when manual intervention might be needed

These changes should make the installation process more reliable and user-friendly, with clearer error messages to help troubleshoot any issues that may still arise. 