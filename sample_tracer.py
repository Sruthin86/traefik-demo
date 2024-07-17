import logging
import time
from jaeger_client import Config
# Importing the library
import psutil

def construct_span(tracer):
    with tracer.start_span('MSULTestSpan') as span:
        span.log_kv({'event': 'test message', 'life': 42})
        print("tracer.tages: ", tracer.tags)
        with tracer.start_span('MSULTestChildSpan', child_of=span) as child_span:
            # perform an operation
            # time.sleep(10)
            span.log_kv({'event': 'here is another event'})
            # span.log_kv({'cpu_usage': psutil.cpu_percent(4)})
        #with tracer.start_span('MSULTestSecondChildSpan', child_of=span) as second_child_span:
        #    # perform an operation
        #    time.sleep(5)
        #    span.log_kv({'event': 'here is another child event'})
        #    span.log_kv({'cpu_usage': psutil.cpu_percent(4)})
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
                'reporting_host': 'tracer',
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
