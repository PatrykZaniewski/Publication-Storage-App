# Publication storage app

Simple application built for „Programming web and mobile applications”. 

# Technology:

- Python 3.7
- Flask
- Javascript
- HTML5
- Docker-compose
- Redis

# Description:

Application is used to publish, edit, share and delete publications and files. Project consists of 3 independent modules:

- web - web client module (receives user’s actions and makes requests to cdn module)
- cdn - REST API module (receives requests from web, collects data from database and makes responses to web)
- database (stores data about users and their publications)

# Security

The main goal was to develop as safe application as possible. To achieve this, i have implemented some security features, for example:
- hashing password multiple times
- using random salt
- anti XSS
- anti CSRF
- restrictive form data validation
- anti DDOS in nginx configuration

# Running an application

To run it, just go to the main directory and type:

    docker-compose -f docker-compose.yml up --build
    
Then, edit your etc/hosts and add:
    
    127.0.0.1 web.company.com
    127.0.0.1 cdn.company.com
    
After that, open your browser and move to "web.company.com".
