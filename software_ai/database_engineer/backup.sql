USE jarvis_knowledge_matrix;

-- ==================================
-- CAMPUS BUILDINGS
-- ==================================
CREATE TABLE campus_buildings (
    building_id INT PRIMARY KEY,
    building_name VARCHAR(100),
    status VARCHAR(20),
    power_level INT,
    occupancy INT
);

INSERT INTO campus_buildings VALUES
(1,'Engineering Center','ONLINE',100,450),
(2,'AI Research Lab','ONLINE',95,120),
(3,'Student Center','ONLINE',100,600),
(4,'Library','ONLINE',100,280),
(5,'Transit Hub','ONLINE',90,75);

-- ==================================
-- JARVIS SUBSYSTEMS
-- ==================================
CREATE TABLE jarvis_subsystems (
    subsystem_id INT PRIMARY KEY,
    subsystem_name VARCHAR(100),
    status VARCHAR(20)
);

INSERT INTO jarvis_subsystems VALUES
(1,'Transportation Control','ONLINE'),
(2,'Building Control','ONLINE'),
(3,'Energy Management','ONLINE'),
(4,'Campus Assistant AI','ONLINE'),
(5,'Access Control','ONLINE');

-- ==================================
-- CAMPUS DEVICES
-- ==================================
CREATE TABLE campus_devices (
    device_id INT PRIMARY KEY,
    device_name VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20)
);

INSERT INTO campus_devices VALUES
(1,'Smart Door Controller','Engineering Center','ONLINE'),
(2,'Camera-C12','Student Center','ONLINE'),
(3,'Temperature Sensor T5','AI Research Lab','ONLINE'),
(4,'Transit Display Board','Transit Hub','ONLINE'),
(5,'Smart Lighting Hub','Library','ONLINE');

-- ==================================
-- AI KNOWLEDGE BASE
-- ==================================
CREATE TABLE ai_knowledge_base (
    id INT PRIMARY KEY,
    question VARCHAR(255),
    answer TEXT
);

INSERT INTO ai_knowledge_base VALUES
(1,
 'Where is orientation?',
 'Orientation is located in the Student Center Auditorium.'
),

(2,
 'Where is the Cybersecurity Lab?',
 'The Cybersecurity Lab is located in the Engineering Center, Room 210.'
),

(3,
 'Where do I get my student ID?',
 'Student IDs are available at the Welcome Desk in the Student Center.'
),

(4,
 'Where is the AI Lab?',
 'The AI Lab is located in the AI Research Building, Room 120.'
),

(5,
 'Where can I get help with registration?',
 'Visit the Student Services Desk in the Student Center.'
);

-- ==================================
-- INCIDENT LOGS
-- ==================================
CREATE TABLE mission_incidents (
    incident_id INT PRIMARY KEY,
    incident_name VARCHAR(100),
    severity VARCHAR(20),
    status VARCHAR(20)
);

INSERT INTO mission_incidents VALUES
(1,'Database Breach','CRITICAL','OPEN'),
(2,'Cloud Service Outage','HIGH','OPEN'),
(3,'AI Hallucination Event','MEDIUM','OPEN');