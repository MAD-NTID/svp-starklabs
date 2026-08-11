DROP DATABASE IF EXISTS starklab_portal;
CREATE DATABASE starklab_portal;
USE starklab_portal;

-- ============================================
-- Interns
-- ============================================

CREATE TABLE interns (
    intern_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(50),
    status ENUM('active','inactive') DEFAULT 'active'
);

INSERT INTO interns
(username,password,first_name,last_name,department,status)
VALUES
('ava','StarkLab2026','Ava','Chen','Artificial Intelligence','active'),
('liam','StarkLab2026','Liam','Patel','Software Engineering','active'),
('maya','StarkLab2026','Maya','Johnson','Cybersecurity','active'),
('noah','StarkLab2026','Noah','Smith','Networking','active'),
('grace','StarkLab2026','Grace','Lee','Hardware','active');

-- ============================================
-- Announcements
-- ============================================

CREATE TABLE announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150),
    message TEXT,
    priority ENUM('High','Medium','Low'),
    posted_date DATE
);

INSERT INTO announcements
(title,message,priority,posted_date)
VALUES
(
'Welcome New Interns',
'Complete your onboarding checklist before Friday.',
'High',
'2026-07-15'
),
(
'AI Safety Training',
'Mandatory training scheduled for Thursday at 2:00 PM.',
'Medium',
'2026-07-18'
),
(
'Robotics Demo',
'Visit Lab B this Friday to see the latest autonomous robots.',
'Low',
'2026-07-20'
);

-- ============================================
-- Projects
-- ============================================

CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    project_code VARCHAR(20),
    project_name VARCHAR(100),
    department VARCHAR(50),
    progress INT,
    status ENUM('Planning','Development','Testing','Completed')
);

INSERT INTO projects
(project_code,project_name,department,progress,status)
VALUES
('ATLAS','Project Atlas','Artificial Intelligence',72,'Development'),
('TITAN','Project Titan','Robotics',54,'Testing'),
('NOVA','Project Nova','Energy',83,'Development'),
('ECHO','Project Echo','Cybersecurity',61,'Development');

-- ============================================
-- Robots
-- ============================================

CREATE TABLE robots (
    robot_id VARCHAR(10) PRIMARY KEY,
    robot_name VARCHAR(100),
    location VARCHAR(100),
    status ENUM('Online','Offline','Maintenance'),
    battery INT
);

INSERT INTO robots
VALUES
('R101','Atlas Rover','Lab A','Online',95),
('R102','Scout','Warehouse','Offline',18),
('R103','Echo','Testing Lab','Maintenance',100),
('R104','Guardian','Main Lobby','Online',87),
('R105','Courier','Engineering Wing','Online',74);