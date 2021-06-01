# Dockerfile for poorconn
#
# Author: Hong Xu <hong@topbug.net>
#
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to
# this Dockerfile to the public domain worldwide. This Dockerfile is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with this Dockerfile. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.
#
# As with all Docker images, the Docker image built from this Dockerfile contains software that are under other
# licenses, including the Poorconn Python package. The license above applies to this Dockerfile only, and does not alter
# the licenses of software included in the Docker image built from this Dockerfile.

# Build the Docker image:
#
#     docker build . -t poorconn
#
# Use the image:
#
#     # Print help message
#     docker run --rm poorconn -h
#     # Run delay_before_sending_upon_acceptance simulation command (try accessing localhost:8000 from the host)
#     docker run -p 8000:8000 --rm poorconn delay_before_sending_upon_acceptance --t=1 --length=1024

FROM python:3.9 AS build

ENV POORCONN_SRC_DIR=/usr/src/poorconn

RUN mkdir -p ${POORCONN_SRC_DIR}

WORKDIR ${POORCONN_SRC_DIR}

COPY . .

# Generate documentation
RUN python -m pip install --no-cache-dir tox && tox -e docs

# Build the Python package
RUN python setup.py sdist && mv dist/poorconn-*.tar.gz dist/poorconn.tar.gz


FROM python:3.9-slim

ENV POORCONN_SRC_DIR=/usr/src/poorconn
ENV POORCONN_SRC_PATH=/usr/src/poorconn.tar.gz

COPY --from=build /usr/src/poorconn/dist/poorconn.tar.gz /usr/src/poorconn.tar.gz

RUN python -m pip install --no-cache-dir ${POORCONN_SRC_PATH}[full]

RUN useradd -m -s /bin/bash poorconn

USER poorconn

WORKDIR /home/poorconn

COPY --from=build ${POORCONN_SRC_DIR}/.tox/docs/_build/html .

ENTRYPOINT ["python", "-m", "poorconn", "-H", "0.0.0.0"]
