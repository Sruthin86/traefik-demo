FROM python:3.12.4
# install jager client
RUN pip install jaeger-client logger psutil
# install
RUN apt update && apt install vim -y
# copy tracer
COPY ./sample_tracer.py ./
# keep the container alive
CMD ["sleep", "infinity"]
