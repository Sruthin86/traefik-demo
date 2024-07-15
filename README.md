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

##### gRPC
* An open-source high performance Remote Procedure Call enabling communication between services
* Efficient in transferring data in binary format
* Request and response are unary (happens in the same call)

##### Trace
* Data execution path through the system.

##### Span
* A logical unit of work that happens within a system that has a start time, end time, and an operation time
* Spans maybe nested, and can have an ordered relationship.

##### Jaeger Agent
* An agent listens for traces over UDP, batches them and sends the traces to Jaeger collector.
* It acts as a traffic regulator or a load balancer between the instrumentation layer and collector
* Jaeger agent is an optional component

##### Jaeger Collector
* A collector runs the received traces traces through a processing pipeline, where the traces are validated, indexed, and stored. 


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

### Run Jaeger as a standalone tracing service
* Run the docker Jaeger docker imager opening the ports which collect data and the UI port
```
docker run -d -p6831:6831/udp -p16686:16686 jaegertracing/all-in-one:1.57 
```
* Install the python jaeger client
```
pip install jaeger-client
```
* Run a sample python script to send spans to Jaeger
```
from jaeger_client import Config


def construct_span(tracer):
    with tracer.start_span('MSULTestSpan') as span:
        span.log_kv({'event': 'test message', 'life': 42})
        print("tracer.tages: ", tracer.tags)
        with tracer.start_span('MSULTestChildSpan', child_of=span) as child_span:
            # perform an operation
            time.sleep(2)
            span.log_kv({'event': 'here is another event'})
        return span


if __name__ == "__main__":
    log_level = logging.DEBUG
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(asctime)s %(message)s', level=log_level)

    config = Config(
        config={ 
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                # Specify the hostname and port number of the Jaeger agent. 
                'reporting_host': 'localhost',
                'reporting_port': 6831,
            },
            'logging': True,
        },
        # Specify the application name.
        service_name="MSUL",
        validate=True
    )

    # this call also sets opentracing.tracer
    tracer = config.initialize_tracer()

    span = construct_span(tracer)

    time.sleep(2)
    tracer.close()
```
### Docker Swarm configuration of Jaeger
* A sample python script exists in this repo which creates sample traces. Build the image that creates sample traces using
```
docker build ./ -t pythontracer    
```
* Deploy the `tracer` stack using
```
docker stack deploy -c docker-compose.tracer.yml jaeger
```
* Run the sample tracer script using
```
docker exec -it `docker ps -qf name="jaeger_sample"` python sample_tracer.py 
```
* The sample traces and spans can be viewed in Jaeger at `http://localhost:16686/`

## Jaeger + Traefik
* Traefik uses OpenTelemetry standard for distributed tracing.
* The traces generated by Traefik include  number of requests received, the requests duration, and more
* The spans inside the traces include requested url, the source ip, status codes, etc.

### Setup
* Add a Jaeger service to collect the traces generated by otlp
```
jaeger:
    image: jaegertracing/all-in-one:1.57
    environment:
      OTEL_TRACES_SAMPLER: 'always_off'
    deploy:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.jaeger.rule=Host(`jaeger.localhost`)"
        - "traefik.http.routers.jaeger.entrypoints=web"
        - "traefik.http.routers.jaeger.service=jaeger"
        - "traefik.http.services.jaeger.loadbalancer.server.port=16686"
    networks:
      - traefik_public
```
* Enable the tracing in the traefik configuration
```
# Enable tracing
      - "--tracing=true"
      # Add a service name which will referenced the UI
      - "--tracing.serviceName=traefik"
      # Trace all requests. Adjust the sampling rate to only trace a percentage of requests
      - "--tracing.sampleRate=1.0"
      - "--tracing.otlp.http=true"
      # Set the end point of the collector
      - "--tracing.otlp.http.endpoint=http://jaeger:4318/v1/traces"
      # Add any custom headers
      - "--tracing.otlp.http.headers.foo=bar"
```
* Bring the traefik and sample applications up by using
```
INSTANCE1=whoami docker stack deploy -c docker-compose.whoami.yml whoami 
INSTANCE2=cats docker stack deploy -c docker-compose.cats.yml cats  
docker stack deploy -c docker-compose.traefik.yml  web
```
* Monitor the traces at `http://jaeger.localhost/`

