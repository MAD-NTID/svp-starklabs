# Database Engineer

# StoryLine

As a result of Dr. Doom's attack across starLab infrastructures, you decided to do an full investigatiion on the database server to ensure that it is still functional.


# Investigation
- Perform a ping check to confirm that the database server is online
- If you are not able to ping the server, the database is offline.
- Contact the Team Circuit on zoom to find out why the database server is offline and what is the plan to fix it.
- Document the findings and prepare a report for the next team to review.

# Restore
- Review the report from the previous team and get a general understanding of what the issue is.
- Wait for the Team Circuit to replace the database server burned RAM and reboot the server
- Once the database server is back online:
    - Create a new database `Name TBD`
    - Import the SQL file `database_backup.sql` into the new database
    - Done
- Document the changes made and prepare a report for the next team to review.

# Test
- Review the report from the previous team and get a general understanding of what the issue is.
- It is now time to verify that the database is online and functional.
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