# Treafik 

* This tutorial is a demonstration of using a single traefik with multiple Docker Swarm stacks

## Docker installation
* Docker is a containerization tool used for developing, packaging and running applications
* Install Docker on the host machine with the [instructions outlined here](https://docs.docker.com/engine/install/)

## Initialize Swarm
* Docker Swarm is a container orchestration tool which consists of multiple services on a given node.
* A Docker host can be a manager or a worker node or both in some cases.
* Initialize a node of 1 (where the manager and the worker are the same node).
```
  docker swarm init
```

## Network Configurations
* Create an external Docker network using.
```
docker network create --driver overlay traefik_public
```
* This will allow Traefik to communicate with other services that are also connected to the traefik_public network.
* Configure services in other Docker Swarm stacks to use the `traefik_public` network
```
# Example
services:
  whoami:
    # ...
    networks:
      - traefik_public
```

## Traefik Stack
* Traefik will the edge router for all the services in the `traefik_public` network. It accepts all requests on port 80 and routes them to different services.
* Deploy the traefik stack using
```
docker stack deploy -c docker-compose.traefik.yml web
```

## Application stack
* TODO
* Deploy the `whoami` stack using
```
docker stack deploy -c docker-compose.yml whoami  
```