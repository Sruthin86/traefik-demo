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
* Deploy the `whoami` stack using
```
INSTANCE1=whoami docker stack deploy -c docker-compose.whoami.yml whoami
```
* Deploy the `cats` stack using
```
INSTANCE2=cats docker stack deploy -c docker-compose.cats.yml cats
```
* Deploy the `dummy` stack using
```
STACK=dummy docker stack deploy -c docker-compose.dummy.yml dummy
```

### Dummy service
* The dummy service is used to block unwanted user agents. In this setup the user agents are defined in the traefik rules and are whitelisted when are from a local ip address. 
* When the matching user agent is not from a whitelisted ip address a 403 response is returned

## Jaeger
### Introduction

#### Glossary
##### Distributed tracing
* Provides insights into how a particular request/service travels and performs in a distributed system.

##### Zipkin
* An open-source tracing system used for monitoring and profiling applications.
* Optimized for http based communications.
* An all-in-one tracing solution implemented in Java
* Requires manual configuration and integration with code to collect data
* Has a wide support for several programming languages ( Java, Python, Ruby, and JavaScript).

##### OpenTelemetry Protocol (otlp)
* An open-source tracing system used for monitoring and profiling applications.
* Automated data collection outside the box.
* Supports Java, Python, Go, .Net.

##### Trace
* Data execution path through the system.

##### Span
* A logical unit of work that happens within a system that has a start time, end time, and an operation time
* Spans maybe nested, and can have an ordered relationship.

#### List of ports
| Port     | Protocol    | Component    | Function |
| :---:    | :---:       |:---:         |:---:     | 
|6831      |UDP          |agent         |accept jaeger.thrift over Thrift-compact protocol (used by most SDKs)|
|6832      |UDP          |agent         |accept jaeger.thrift over Thrift-binary protocol (used by Node.js SDK)|
|5778      |HTTP         |agent         |serve configs (sampling, etc.)|
|16686     |HTTP         |query         |serve frontend|
|4317      |HTTP         |collector     |accept OpenTelemetry Protocol (OTLP) over gRPC|
|4318      |HTTP         |collector     |accept OpenTelemetry Protocol (OTLP) over HTTP|
|14268     |HTTP         |collector     |accept jaeger.thrift directly from clients|
|14250     |HTTP         |collector     |accept model.proto|
|9411      |HTTP         |collector     |Zipkin compatible endpoint (optional)|

* Key terms
* Installation steps
* Use cases
* Demo/Troubleshooting
* Alternatives
