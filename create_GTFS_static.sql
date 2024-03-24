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
create table trips (route_id varchar(20),service_id INT,trip_id varchar(20) PRIMARY KEY,trip_headsign varchar(50),trip_short_name varchar(50),direction_id varchar(10),block_id varchar(50),shape_id varchar(20),
	FOREIGN KEY (route_id) REFERENCES routes(route_id),
	FOREIGN KEY (service_id) REFERENCES calendar(service_id));
ALTER TABLE stop_times ADD FOREIGN KEY (trip_id) REFERENCES trips(trip_id);
ALTER TABLE stop_times ADD FOREIGN KEY (stop_id) REFERENCES stops(stop_id);


