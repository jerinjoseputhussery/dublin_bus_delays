create database dublin_bus;
use dublin_bus;
create table agency (agency_id INT PRIMARY KEY,agency_name varchar(50),agency_url varchar(100),agency_timezone varchar(50));
create table calendar (service_id INT PRIMARY KEY,monday INT,tuesday INT,wednesday INT,thursday INT,friday INT,saturday INT,sunday INT,start_date DATE,end_date DATE);
create table calendar_dates (service_id INT,date DATE,exception_type INT,
	FOREIGN KEY (service_id) REFERENCES calendar(service_id));
create table feed_info (feed_publisher_name varchar(100),feed_publisher_url varchar(100),feed_lang varchar(20),feed_start_date DATE,feed_end_date DATE,feed_version varchar(100));
create table routes (route_id varchar(20) PRIMARY KEY,agency_id INT,route_short_name varchar(20),route_long_name varchar(100),route_desc varchar(100),route_type varchar(20),route_url varchar(100),route_color varchar(100),route_text_color varchar(100),
	FOREIGN KEY (agency_id) REFERENCES agency(agency_id));
create table shapes (shape_id varchar(20),shape_pt_lat varchar(20),shape_pt_lon varchar(20),shape_pt_sequence INT,shape_dist_traveled FLOAT);
create table stop_times (trip_id varchar(20),arrival_time TIME,departure_time TIME,stop_id varchar(20),stop_sequence INT,stop_headsign varchar(50),pickup_type INT,drop_off_type INT,timepoint INT,
	PRIMARY KEY (trip_id,stop_id));
create table stops (stop_id varchar(20) PRIMARY KEY,stop_code INT,stop_name varchar(50),stop_desc varchar(100),stop_lat varchar(20),stop_lon varchar(20),zone_id varchar(100),stop_url varchar(100),location_type varchar(100),parent_station varchar(100));
create table trips (route_id varchar(20),service_id INT,trip_id varchar(20) PRIMARY KEY,trip_headsign varchar(50),trip_short_name varchar(50),direction_id varchar(10),block_id varchar(200),shape_id varchar(20),
	FOREIGN KEY (route_id) REFERENCES routes(route_id),
	FOREIGN KEY (service_id) REFERENCES calendar(service_id));
ALTER TABLE stop_times ADD FOREIGN KEY (trip_id) REFERENCES trips(trip_id);
ALTER TABLE stop_times ADD FOREIGN KEY (stop_id) REFERENCES stops(stop_id);

--ROUTE MAPPING TABLE
create table route_mapping (route_id varchar(20),route_short_name varchar(20), is_active int, primary key(route_short_name,route_id));


--SEQUENCE FOR ENTRY_ID
CREATE SEQUENCE entry_id_seq start with 1 increment by 1;

--DYNAMIC TABLES
Create table route_delays (entry_id int, route_id varchar(20), direction_id varchar(10), entry_timestamp datetime, current_delay int, avg_route_delay int,
PRIMARY KEY (entry_id,route_id,direction_id,entry_timestamp));
Create table delays(entry_id int, entry_timestamp datetime, current_delay int, avg_delay int, primary key(entry_id,entry_timestamp));
Create table weather (entry_id int, location varchar(200), entry_timestamp datetime,temperature_2m	FLOAT,relative_humidity_2m int,apparent_temperature	FLOAT,is_day int,precipitation int,rain int,showers int, snowfall int, weather_code int, cloud_cover int, pressure_msl FLOAT, surface_pressure FLOAT, wind_speed_10m FLOAT,wind_direction_10m int, wind_gusts_10m FLOAT, avg_temperature_2m	FLOAT, avg_relative_humidity_2m int, avg_apparent_temperature	FLOAT, avg_precipitation int, avg_rain int, avg_showers int, avg_snowfall int, avg_cloud_cover int, avg_pressure_msl FLOAT, avg_surface_pressure FLOAT, avg_wind_speed_10m FLOAT, avg_wind_direction_10m int, avg_wind_gusts_10m FLOAT, primary key(entry_id,entry_timestamp));
create table weather_codes( code int primary key,code_description varchar(100), code_count int, avg_delay int);

--INSERT QUERIES TO weather_codes table
insert into weather_codes values(0,'Clear sky',0,0);
insert into weather_codes values(1,'Mainly clear',0,0);
insert into weather_codes values(2,'partly cloudy',0,0);
insert into weather_codes values(3,'overcast',0,0);
insert into weather_codes values(45,'Fog',0,0);
insert into weather_codes values(48,'depositing rime fog',0,0);
insert into weather_codes values(51,'Light Drizzle',0,0);
insert into weather_codes values(53,'Moderate Drizzle',0,0);
insert into weather_codes values(55,'Dense Drizzle',0,0);
insert into weather_codes values(56,'Light Freezing Drizzle',0,0);
insert into weather_codes values(57,'Dense Freezing Drizzle',0,0);
insert into weather_codes values(61,'Slight Rain',0,0);
insert into weather_codes values(63,'Moderate Rain',0,0);
insert into weather_codes values(65,'Heavy Rain',0,0);
insert into weather_codes values(66,'Light Freezing Rain',0,0);
insert into weather_codes values(67,'heavy Freezing Rain',0,0);
insert into weather_codes values(71,'Slight Snow fall',0,0);
insert into weather_codes values(73,'moderate Snow fall',0,0);
insert into weather_codes values(75,'Heavy Snow fall',0,0);
insert into weather_codes values(77,'Snow grains',0,0);
insert into weather_codes values(80,'Slight Rain showers',0,0);
insert into weather_codes values(81,'Moderate Rain showers',0,0);
insert into weather_codes values(82,'Violent Rain showers',0,0);
insert into weather_codes values(85,'Slight Snow showers',0,0);
insert into weather_codes values(86,'Heavy Snow showers',0,0);
insert into weather_codes values(95,'Slight or moderate Thunderstorm',0,0);
insert into weather_codes values(96,'Thunderstorm with slight hail',0,0);
insert into weather_codes values(99,'Thunderstorm with heavy hail',0,0);

--TRIGGERS
CREATE TRIGGER weather_code_trigger
ON weather
AFTER INSERT
AS
BEGIN    
    UPDATE weather_codes SET code_count = code_count + 1 WHERE code=(SELECT weather_code FROM inserted);	
END;

