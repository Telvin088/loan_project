-- Create the database
CREATE DATABASE loan_auth;

-- Use the database
USE loan_auth;

-- Create the users table
CREATE TABLE
    users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        profile_photo VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        session_id VARCHAR(255),
        amount DECIMAL(10, 2) DEFAULT 0.00,
        status VARCHAR(20) DEFAULT 'pending',
        allocated_amount DECIMAL(10, 2) DEFAULT 0.00,
        allocation_date DATE
    );

use loan_auth;

INSERT INTO
    users (
        username,
        email,
        phone,
        profile_photo,
        password,
        session_id
    )
VALUES
    (
        'john_doe',
        'john.doe@example.com',
        '123-456-7890',
        'static\uploads\106774.jpg',
        'password123',
        '123e4567-e89b-12d3-a456-426614174000'
    ),
    (
        'jane_smith',
        'jane.smith@example.com',
        '987-654-3210',
        'static\uploads\ducks2.jpg',
        'password456',
        '456e7890-e12b-34c5-d678-987514175000'
    ),
    (
        'alice_green',
        'alice.green@example.com',
        '555-555-5555',
        'static\uploads\v1.jpg',
        'password789',
        '789e1234-e56b-78d9-e012-345614176000'
    )
    -- Add more records as needed
;

-- Create the newsletter_subscriptions table
use loan_auth;

CREATE TABLE
    newsletter_subscriptions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

INSERT INTO
    newsletter_subscriptions (session_id, email)
VALUES
    (
        '123e4567-e89b-12d3-a456-426614174000',
        'john.doe@example.com'
    ),
    (
        '456e7890-e12b-34c5-d678-987514175000',
        'jane.smith@example.com'
    ),
    (
        '789e1234-e56b-78d9-e012-345614176000',
        'alice.green@example.com'
    )
    -- Add more records as needed
;

USE loan_auth;

-- Create the profile table
CREATE TABLE
    profile (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        middle_name VARCHAR(255),
        last_name VARCHAR(255) NOT NULL,
        identification VARCHAR(50) NOT NULL,
        kra_pin VARCHAR(50) NOT NULL,
        religion VARCHAR(50) NOT NULL,
        dob DATE NOT NULL,
        telephone VARCHAR(20) NOT NULL,
        gender VARCHAR(10) NOT NULL,
        marital_status VARCHAR(20) NOT NULL,
        disability VARCHAR(10) NOT NULL,
        employed VARCHAR(10) NOT NULL,
        education VARCHAR(50) NOT NULL,
        profile_photo VARCHAR(255),
        po_box VARCHAR(50) NOT NULL,
        postal_code VARCHAR(20) NOT NULL,
        town VARCHAR(255) NOT NULL,
        county VARCHAR(255) NOT NULL,
        constituency VARCHAR(255) NOT NULL,
        ward VARCHAR(255) NOT NULL,
        session_id VARCHAR(255) NOT NULL
    );

use loan_auth;

CREATE TABLE
    user_deposits (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        amount INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

USE loan_auth;

-- Create the table
CREATE TABLE
    IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email_address VARCHAR(100) NOT NULL,
        phone_number VARCHAR(20),
        city VARCHAR(50),
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

use loan_auth;

CREATE TABLE
    allocation_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

use loan_auth;

CREATE TABLE
    loan_applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL,
        session_id VARCHAR(50) NOT NULL,
        loan_type ENUM ('emergency', 'normal', 'short') NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        interest INT DEFAULT 8, -- Assuming '0' is a default value
        refund INT DEFAULT 0, -- Assuming '0' is a default value
        allocated_amount DECIMAL(10, 2) DEFAULT 0.00,
        application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


use loan_auth;
create table total_interests(
    id int AUTO_INCREMENT PRIMARY KEY,
    totals int
)