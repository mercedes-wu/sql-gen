FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV PYTHON_VERSION=3.10

RUN python -m pip install --upgrade pip

RUN apt-get update && apt-get -y install --no-install-recommends postgresql-client

CMD ["/bin/bash"]