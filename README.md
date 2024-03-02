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
* #TODO
* Deploy the `whoami` stack using
```
docker stack deploy -c docker-compose.yml whoami  
```

## Glossary
* **Provides** discover services that live on the infrastructure.
* **Entrypoints** listen for incoming traffic(ports, ...)
* **Routers** analyze the requests (host, path, headers, ssl, ...)
* **Services** forward the request to your services (load balancing, ...)
* **Middlewares** may update the request or make decisions based on the request (auth, rate limiting, ip limiting, ...)

## Traefik Help

### Routers

* Breakdown of Traefik router label
```
traefik.http.routers.<router_name>.rule

# breakdown
traefik - docker service
http - protocol (can be http, tcp or udp)
routers - Traefik configuration (can be services, middlewares)
<router_name> - user defined name
rule -  option (what are we doing to the router)

# examples
traefik.http.routers.whoami.rule=Host(`whoami.localhost`)
traefik.http.routers.whoami.entrypoints=web,ep2,ep3
```
* For each service Traefik creates a service and router. When no rules are set Traefik assigns a default rule
* Priority of the rule is set based on the length of the rule unless explicitly set.
* List of Router configurations can be found [here](https://doc.traefik.io/traefik/routing/routers/)

### Entrypoints
* 
* All entrypoints are assigned to all routers unless explicitly set.

### Services
* #TODO
* A service can be assigned to multiple to multiple Routers
* Breakdown of Traefik router label
* List of available Services can be found here #TODO
```
traefik.http.services.<service_name>.option

# breakdown
traefik - docker service
http - protocol (can be http, tcp or udp)
services - Traefik configuration (can be services, middlewares)
<services_name> - user defined name


# examples
traefik.http.routers.whoami.loadbalancer.server.port=80
```
#### Load Balancers
* Each service has its own Load Balancer, it is assigned by default
* If we scale the application to more than one replicas it routes the requests to the replicas using Round Robin technique.
* Load Balancers can be configured with Health Checks to monitor the heath of the Server.
* The target of the Load Balancer is called the server 

### Middlewares
* Attached to Routers.
* Means of tweaking requests before they reach services.
* List of available HTTP Middlewares can be found [here](https://doc.traefik.io/traefik/middlewares/http/overview/)