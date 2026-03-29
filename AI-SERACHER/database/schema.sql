-- AI Hotel Booking Chatbot Database Schema
-- CS331 Project - Fall 2025

-- Create Database
CREATE DATABASE IF NOT EXISTS hotel_booking_ai;
USE hotel_booking_ai;

-- ============================================
-- Table 1: hotels
-- ============================================
CREATE TABLE IF NOT EXISTS hotels (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(500) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'Saudi Arabia',
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    description TEXT,
    star_rating DECIMAL(2, 1) CHECK (star_rating >= 1 AND star_rating <= 5),
    amenities JSON,  -- Store as JSON array: ["WiFi", "Pool", "Parking"]
    price_per_night DECIMAL(10, 2) NOT NULL,
    google_place_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_price (price_per_night),
    INDEX idx_location (latitude, longitude)
);

-- ============================================
-- Table 2: reviews
-- ============================================
CREATE TABLE IF NOT EXISTS reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT NOT NULL,
    guest_name VARCHAR(100) NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT NOT NULL,
    sentiment_score DECIMAL(3, 2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE,
    INDEX idx_hotel_id (hotel_id),
    INDEX idx_sentiment (sentiment_score)
);

-- ============================================
-- Table 3: landmarks
-- ============================================
CREATE TABLE IF NOT EXISTS landmarks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    alternative_names JSON,  -- Store alternative spellings: ["Al-Haram", "AlHaram", "Grand Mosque"]
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    city VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_city (city),
    INDEX idx_name (name)
);

-- ============================================
-- Insert Sample Data for Testing
-- ============================================

-- Sample Hotels in Makkah
INSERT INTO hotels (name, address, city, country, latitude, longitude, description, star_rating, amenities, price_per_night, google_place_id) VALUES
('Grand Makkah Hotel', 'Ibrahim Al Khalil Street, Makkah', 'Makkah', 'Saudi Arabia', 21.4225, 39.8262, 'Luxury hotel near Al-Haram with stunning views', 5.0, '["WiFi", "Pool", "Parking", "Gym", "Restaurant", "Room Service"]', 800.00, NULL),
('Al-Safwa Tower', 'Ajyad Street, Makkah', 'Makkah', 'Saudi Arabia', 21.4190, 39.8240, 'Modern hotel with excellent amenities close to the Holy Mosque', 4.5, '["WiFi", "Parking", "Restaurant", "Room Service"]', 600.00, NULL),
('Makkah Clock Tower', 'Abraj Al Bait, Makkah', 'Makkah', 'Saudi Arabia', 21.4189, 39.8256, 'Iconic hotel with direct access to Haram', 5.0, '["WiFi", "Pool", "Gym", "Restaurant", "Room Service", "Spa"]', 1200.00, NULL),
('Budget Inn Makkah', 'Aziziyah District, Makkah', 'Makkah', 'Saudi Arabia', 21.4350, 39.8450, 'Affordable accommodation with basic amenities', 3.0, '["WiFi", "Parking"]', 250.00, NULL),
('Al-Noor Hotel', 'Jarwal Street, Makkah', 'Makkah', 'Saudi Arabia', 21.4210, 39.8275, 'Comfortable hotel near Haram with great service', 4.0, '["WiFi", "Parking", "Restaurant", "Breakfast"]', 450.00, NULL),
('Hilton Makkah', 'King Abdul Aziz Road, Makkah', 'Makkah', 'Saudi Arabia', 21.4200, 39.8280, 'International chain hotel with premium facilities', 5.0, '["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Spa", "Room Service"]', 950.00, NULL),
('Economy Stay Makkah', 'Al Mansour Street, Makkah', 'Makkah', 'Saudi Arabia', 21.4400, 39.8500, 'Budget-friendly option for pilgrims', 2.5, '["WiFi"]', 180.00, NULL),
('Royal Palace Hotel', 'Ibrahim Al Khalil Street, Makkah', 'Makkah', 'Saudi Arabia', 21.4230, 39.8265, 'Elegant hotel with traditional hospitality', 4.5, '["WiFi", "Parking", "Restaurant", "Gym", "Room Service"]', 700.00, NULL);

-- Sample Hotels in Madinah
INSERT INTO hotels (name, address, city, country, latitude, longitude, description, star_rating, amenities, price_per_night, google_place_id) VALUES
('Madinah Oberoi', 'King Faisal Road, Madinah', 'Madinah', 'Saudi Arabia', 24.4672, 39.6108, 'Luxury accommodation near Prophet\'s Mosque', 5.0, '["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Spa"]', 850.00, NULL),
('Al-Aqeeq Hotel', 'Quba Road, Madinah', 'Madinah', 'Saudi Arabia', 24.4700, 39.6150, 'Comfortable hotel with excellent location', 4.0, '["WiFi", "Parking", "Restaurant", "Breakfast"]', 400.00, NULL),
('Madinah Budget Inn', 'Al-Hijra Street, Madinah', 'Madinah', 'Saudi Arabia', 24.4800, 39.6200, 'Affordable stay for budget travelers', 3.0, '["WiFi", "Parking"]', 220.00, NULL);

-- Sample Hotels in Riyadh
INSERT INTO hotels (name, address, city, country, latitude, longitude, description, star_rating, amenities, price_per_night, google_place_id) VALUES
('Riyadh Marriott', 'King Fahd Road, Riyadh', 'Riyadh', 'Saudi Arabia', 24.7136, 46.6753, 'Business hotel in the heart of Riyadh', 5.0, '["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Business Center"]', 650.00, NULL),
('Al-Faisaliah Hotel', 'King Fahd Road, Riyadh', 'Riyadh', 'Saudi Arabia', 24.6900, 46.6850, 'Iconic tower hotel with luxury amenities', 5.0, '["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Spa", "Room Service"]', 900.00, NULL),
('Riyadh Express', 'Olaya Street, Riyadh', 'Riyadh', 'Saudi Arabia', 24.7200, 46.6800, 'Modern hotel for business travelers', 4.0, '["WiFi", "Gym", "Parking", "Restaurant"]', 380.00, NULL);

-- Sample Hotels in Jeddah
INSERT INTO hotels (name, address, city, country, latitude, longitude, description, star_rating, amenities, price_per_night, google_place_id) VALUES
('Jeddah Hilton', 'Corniche Road, Jeddah', 'Jeddah', 'Saudi Arabia', 21.5433, 39.1728, 'Beachfront hotel with stunning Red Sea views', 5.0, '["WiFi", "Pool", "Gym", "Parking", "Restaurant", "Beach Access"]', 750.00, NULL),
('Red Sea Palace', 'Al-Hamra District, Jeddah', 'Jeddah', 'Saudi Arabia', 21.5500, 39.1800, 'Elegant hotel near shopping districts', 4.5, '["WiFi", "Pool", "Parking", "Restaurant", "Room Service"]', 550.00, NULL),
('Jeddah Inn', 'Al-Balad, Jeddah', 'Jeddah', 'Saudi Arabia', 21.4858, 39.1925, 'Historic area hotel with cultural charm', 3.5, '["WiFi", "Parking", "Restaurant"]', 300.00, NULL);

-- Sample Hotels in Yanbu (NEW - Premium Hotels)
INSERT INTO hotels (name, address, city, country, latitude, longitude, description, star_rating, amenities, price_per_night, google_place_id) VALUES
('Yanbu Royal Palace Hotel', 'North Corniche Road, Yanbu', 'Yanbu', 'Saudi Arabia', 24.1512, 38.0680, 'Luxury beachfront resort with stunning Red Sea views', 5.0, '["WiFi", "Pool", "Gym", "Spa", "Fine Dining", "Beach Access"]', 1200.00, NULL),
('Yanbu Hilton Resort', 'South Beach, Yanbu', 'Yanbu', 'Saudi Arabia', 24.1380, 38.0620, 'Upscale beachfront hotel with excellent service', 4.5, '["WiFi", "Pool", "Gym", "Restaurant", "Beach Access", "Business Center"]', 850.00, NULL),
('Yanbu Pearl Marina Hotel', 'Marina District, Yanbu', 'Yanbu', 'Saudi Arabia', 24.1450, 38.0750, 'Modern hotel with marina views and excellent amenities', 4.0, '["WiFi", "Pool", "Gym", "Restaurant", "Marina View"]', 600.00, NULL),
('Yanbu Premium Boutique', 'City Center, Yanbu', 'Yanbu', 'Saudi Arabia', 24.1520, 38.0700, 'Stylish boutique hotel in city center', 4.0, '["WiFi", "Gym", "Restaurant", "Rooftop Bar", "Parking"]', 550.00, NULL);

-- Sample Reviews for Hotels
INSERT INTO reviews (hotel_id, guest_name, rating, review_text, sentiment_score) VALUES
-- Grand Makkah Hotel reviews
(1, 'Ahmed Ali', 5, 'Excellent hotel! Very clean rooms and the location is perfect. Staff was extremely helpful and friendly.', 0.85),
(1, 'Fatima Hassan', 5, 'The view of the Haram from our room was breathtaking. Highly recommend this hotel!', 0.90),
(1, 'Mohammed Saeed', 4, 'Great hotel overall. The only downside was the breakfast could be better.', 0.60),
(1, 'Sarah Ibrahim', 5, 'Wonderful experience. The proximity to Al-Haram is unbeatable. Very comfortable stay.', 0.88),

-- Al-Safwa Tower reviews
(2, 'Omar Khalid', 4, 'Good hotel with decent amenities. Close to the mosque which is very convenient.', 0.65),
(2, 'Aisha Mohammed', 5, 'Loved everything about this place! Staff was amazing and rooms were spotless.', 0.92),
(2, 'Abdullah Yousef', 3, 'Average experience. Room was okay but service was slow.', 0.20),

-- Budget Inn Makkah reviews
(4, 'Hassan Ahmed', 4, 'Great value for money! Clean and simple. Perfect for budget travelers.', 0.70),
(4, 'Maryam Ali', 3, 'Basic amenities but does the job. Location is a bit far from Haram.', 0.30),
(4, 'Khalid Nasser', 4, 'Good budget option. WiFi works well and staff is friendly.', 0.68),

-- Al-Noor Hotel reviews
(5, 'Nora Abdullah', 5, 'Excellent location and very clean. The breakfast was delicious!', 0.85),
(5, 'Ibrahim Fahad', 4, 'Nice hotel with good service. Parking was convenient.', 0.72),

-- Hilton Makkah reviews
(6, 'Sultan Mohammed', 5, 'Five-star experience all the way! The gym and pool were excellent.', 0.95),
(6, 'Layla Hassan', 5, 'Luxury at its best. The spa was amazing and staff was very professional.', 0.93),
(6, 'Faisal Ahmed', 4, 'Great hotel but quite expensive. Worth it for the amenities though.', 0.65),

-- Madinah Oberoi reviews
(9, 'Jamal Rashid', 5, 'Outstanding hotel! The service was impeccable and location perfect.', 0.90),
(9, 'Amina Khalid', 5, 'Loved our stay here. Very close to the Prophet\'s Mosque. Highly recommend!', 0.88),

-- Riyadh Marriott reviews
(12, 'Tariq Ali', 4, 'Good business hotel. Conference facilities were excellent.', 0.70),
(12, 'Noura Said', 4, 'Comfortable stay for business trip. WiFi was fast and reliable.', 0.68),

-- Jeddah Hilton reviews
(15, 'Waleed Omar', 5, 'Beautiful beachfront location! The pool area was fantastic.', 0.87),
(15, 'Huda Fahad', 5, 'Wonderful hotel with stunning views of the Red Sea. Very relaxing.', 0.91),

-- Red Sea Palace reviews
(16, 'Yasser Mohammed', 4, 'Great hotel near shopping areas. Rooms were spacious and clean.', 0.75),
(16, 'Lina Ahmed', 4, 'Good experience overall. Restaurant food was delicious.', 0.72);

-- Sample Landmarks
INSERT INTO landmarks (name, alternative_names, latitude, longitude, city, description) VALUES
('Al-Haram Al-Makki', '["Al-Haram", "AlHaram", "Grand Mosque", "Sacred Mosque", "Masjid al-Haram", "Holy Mosque", "Kaaba"]', 21.4225, 39.8262, 'Makkah', 'The holiest site in Islam, home to the Kaaba'),
('Prophet\'s Mosque', '["Al-Masjid an-Nabawi", "Masjid Nabawi", "Prophet Mosque", "Prophets Mosque"]', 24.4672, 39.6108, 'Madinah', 'The second holiest site in Islam, burial place of Prophet Muhammad'),
('Mount Arafat', '["Jabal Arafat", "Mount Arafah", "Arafat"]', 21.3546, 39.9839, 'Makkah', 'Sacred hill where Prophet Muhammad gave his Farewell Sermon'),
('Quba Mosque', '["Masjid Quba", "Quba"]', 24.4416, 39.6191, 'Madinah', 'The first mosque built in Islam'),
('Kingdom Centre', '["Kingdom Tower", "Al-Mamlaka Tower"]', 24.7114, 46.6747, 'Riyadh', 'Iconic skyscraper and shopping center in Riyadh'),
('Jeddah Corniche', '["Corniche", "Jeddah Waterfront"]', 21.5433, 39.1728, 'Jeddah', 'Scenic coastal resort area along the Red Sea'),
('Masjid al-Jinn', '["Jinn Mosque", "Mosque of Jinn"]', 21.4410, 39.8295, 'Makkah', 'Historic mosque in Makkah'),
('Jabal al-Nour', '["Mountain of Light", "Cave of Hira"]', 21.4579, 39.8595, 'Makkah', 'Mountain containing the Cave of Hira where Prophet Muhammad received first revelation');

-- ============================================
-- Useful Queries for Testing
-- ============================================

-- Get all hotels in Makkah
-- SELECT * FROM hotels WHERE city = 'Makkah';

-- Get hotels with WiFi and Pool
-- SELECT * FROM hotels WHERE JSON_CONTAINS(amenities, '"WiFi"') AND JSON_CONTAINS(amenities, '"Pool"');

-- Get hotels under 500 SAR
-- SELECT * FROM hotels WHERE price_per_night < 500 ORDER BY price_per_night;

-- Get hotels with average review rating above 4
-- SELECT h.*, AVG(r.rating) as avg_rating 
-- FROM hotels h 
-- LEFT JOIN reviews r ON h.id = r.hotel_id 
-- GROUP BY h.id 
-- HAVING avg_rating >= 4;

-- Get all reviews for a specific hotel
-- SELECT * FROM reviews WHERE hotel_id = 1 ORDER BY created_at DESC;

-- Get average sentiment score for a hotel
-- SELECT hotel_id, AVG(sentiment_score) as avg_sentiment FROM reviews GROUP BY hotel_id;

-- Search landmarks by alternative names
-- SELECT * FROM landmarks WHERE JSON_CONTAINS(alternative_names, '"AlHaram"');

-- ============================================
-- Notes:
-- ============================================
-- 1. Make sure to update sentiment_score after inserting reviews (can be done via Python)
-- 2. Amenities are stored as JSON arrays for flexibility
-- 3. Alternative names for landmarks help with fuzzy matching
-- 4. Indexes are added for frequently queried columns to improve performance
-- 5. Use DECIMAL for latitude/longitude to maintain precision
