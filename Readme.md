# Project Setup Guide

## Overview

This guide provides step-by-step instructions on how to set up and run the project locally. Ensure that you follow each step carefully to avoid any issues.

### Dependencies

Make sure to create and install the following dependencies. In case of conflicts, only install the specified versions. The project is designed to work with Python 3.10.

- **requests** = 2.31.0
- **asyncio** = 3.4.3
- **uuid** = 1.30
- **websockets** = 12.0
- **redis** = 5.0.1
- **scikit-learn** = 1.3.2
- **nltk** = 3.8.1
- **sumy** = 0.11.0
- **langchain** = 0.0.239
- **sentence-transformers** = 2.2.2

### Docker Compose Installation

Before proceeding, make sure you have Docker Compose installed. If not, you can install it from the following URL: [Docker Compose Installation](https://docs.docker.com/engine/install/ubuntu/)

### Redis Server Installation

Install the Redis server using Docker with the following command:

```bash
docker run -p 6379:6379 redis/redis-stack-server:latest
```

### Running the Project

Before running the main.py change the Chatserver.envVars file make sure that the redis is set to localhost

1. Run the `main.py` file.

```bash
python main.py
```

2. Open `testserver.html` in your preferred web browser.

3. Add the following details for organization and agent:

   - **Organization ID**: b17f239d868e5f6b9420682583034dad
   - **Agent ID**: f215b4be73975b87acb4260afbc1ab23

4. Start a conversation to test the functionality.

**Note:** Ensure that the Redis server is running in the background for this iteration to work properly.

## Additional Information

For any issues or questions, refer to the project documentation or contact the project maintainers. Happy coding!


## New Update the code is changed to use FASTAPI and UVICORN for websocket handling , all the issues related to websocket is now resolved 

### Running the newer version using Dockercompose 
Before running the main.py change the Chatserver.envVars file make sure that the redis is set to redis_server


```
docker compose up --build
```
The server will be running on localhost:5000 port and automatically redis will be setup in the 
backend no need to install or setup redis manually. 

## Sample DrugName and Quetion to test out 
- Alcide UDDERgold Platinum 
   - How does it work ?
   - where to use it ?
   - Where to store it ?
   

