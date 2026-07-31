# Database Engineer

The attacker destroyed the database server RAM as well as
deleted the database.

# Investigation
- Discovered that the database is not online
    - Ping the database server and it is not responding
- Coordingate with the Zoom person with Team circuit to find out why the database is offline

# Restore
- Wait for the Team Circuit to replace the database server RAM and reboot the server
- Once the database server is back online:
    - Create a new database `Name TBD`
    - Import the SQL file `database_backup.sql` into the new database
    - Done

# Test
 - Verify that the database is online
 - Verify that the database `name exist` and the tables are present

# Secure Hands off
- Create a documentation on what to do if the situation happens again
- Create a backup of the database
- Create a backup plan

# Possible hands off example

DATABASE INCIDENT REPORT

Root Cause:
[X] RAM Failure

Recovery Actions:
[X] Hardware repaired
[X] Database recreated
[X] Backup restored
 
Future Protection:
[X] Daily Backup Enabled
[X] Store backup in 3 different formats
 
15
Status:
16
[X] DATABASE ONLINE