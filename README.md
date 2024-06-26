
# Dublin Bus Delay Dashboard
A real-time delay dashboard created in Python Dash that displays various Dublin Bus delay insights and weather insights. The idea is to analyze from the dashboard whether there is any correlation between the Dublin weather data and Dublin Bus delays.

## Github Link
The repository is getting updated throughout the development by the developer.

[dublin_bus_delays](https://github.com/jerinjoseputhussery/dublin_bus_delays)
## How to setup

Before setting up, make sure you have all the below prerequisite are in place:
###### • Python 3.11 or greater
###### • Connectivity to an SQL Server 2022
\
Once cloned the repo, make sure to install all the requirements from dashboard/requirements.txt

Next, create below three configuration files and configure them based on the example files

    config.py
    static_loader_config.py
    dashboard/config.py


Execute the below SQL script in the SQL Server database to create the database and tables. 

    create_GTFS_static.sql



## How to execute locally

There are two different module to be executed to run this project.

#### 1. Extraction service
The  extraction services can be executed by following command:

    python app.py
#### 2. Dashboard services
The dashboard services can be executed by the following command:

    cd dashboard/
    python app.py
Once this is done, open a browser and visit following URL:

    http://127.0.0.1:8050/



## Deployment Link

The extraction services are deployed on Azure virtual machine and the SQL Server database is set up on the same machine.


The dashboard is deployed on AWS EC2. Follow the deployment  
[link](https://engaged-magnetic-tarpon.ngrok-free.app/) to access the dublin bus delay dashboard.

