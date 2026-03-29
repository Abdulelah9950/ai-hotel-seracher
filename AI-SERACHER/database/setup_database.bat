@echo off
echo ========================================
echo Setting Up Hotel Booking AI Database
echo ========================================
echo.
echo This will create the database and insert sample hotels.
echo You will be prompted for your MySQL root password.
echo.
pause

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < "C:\Users\abomo\OneDrive\Desktop\College\471-Semester\CS331\CS331Project\CS331_Project\database\schema.sql"

echo.
echo ========================================
echo Database setup complete!
echo ========================================
echo.
echo To verify, you can run:
echo mysql -u root -p -e "USE hotel_booking_ai; SELECT COUNT(*) FROM hotels;"
echo.
pause
