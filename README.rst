.. readme-roles

.. role:: doc(literal)
.. role:: func(literal)
.. role:: mod(literal)

.. readme-main

Poorconn: Simulating Poor Network Conditions
============================================

.. image:: https://img.shields.io/pypi/v/poorconn.svg
   :target: https://pypi.python.org/pypi/poorconn
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/poorconn.svg
   :target: https://pypi.python.org/pypi/poorconn
   :alt: PyPI - Python Versions

.. image:: https://img.shields.io/pypi/implementation/poorconn
   :target: https://pypi.python.org/pypi/poorconn
   :alt: PyPI - Implementation

.. image:: https://img.shields.io/badge/-Documentation-informational
   :target: https://poorconn.topbug.net
   :alt: Documentation

.. image:: https://img.shields.io/pypi/l/poorconn
   :target: https://gitlab.com/xuhdev/poorconn/-/blob/master/COPYING
   :alt: PyPI - License

.. image:: https://gitlab.com/xuhdev/poorconn/badges/master/pipeline.svg
   :target: https://gitlab.com/xuhdev/poorconn/-/commits/master
   :alt: Pipeline Status

.. image:: https://gitlab.com/xuhdev/poorconn/badges/master/coverage.svg
   :target: https://gitlab.com/xuhdev/poorconn/-/commits/master
   :alt: Coverage

Poorconn is a Python package that simulates poor network conditions. It is suitable for testing purposes, for both
Python and non-Python projects.

It is capable of simulating the following poor network conditions:

- Throttled network connections. (:func:`delay_before_sending`, :func:`delay_before_sending_upon_acceptance`)
- Servers that cut off connections immediately upon accepting them. (:func:`close_upon_acceptance`)
- Connections that are initially slow, but become normal subsequently. (:func:`delay_before_sending_once`,
  :func:`delay_before_sending_upon_acceptance_once`)


.. _quickstart:

Quickstart
----------

Install this package via

.. code-block:: console

   $ pip install 'poorconn[full]'  # or "pip install poorconn" if you don't need pytest support

Command Line Usage
~~~~~~~~~~~~~~~~~~

The following example starts a local HTTP server at port 8000 that hosts static files at the current working directory.
It always closes connections upon accepting them:

.. code-block:: console

   $ python -m poorconn -H localhost -p 8000 close_upon_acceptance

In this command, ``python -m poorconn`` invokes Poorconn's command line entrypoint, ``-H localhost`` specifies
the hostname, ``-p 8000`` specifies the port number, and ``close_upon_acceptance`` is a *simulation command* that
simulates a specific poor network conditions, which in this case is closing connections upon accepting them.

After running the command above, connections from a client would establish but fail to communicate subsequently:

.. code-block:: console

   $ wget -t 1 http://127.0.0.1:8000
   Connecting to 127.0.0.1:8000... connected.
   HTTP request sent, awaiting response... No data received.
   Giving up.

For another example, to start a local HTTP server that always throttle connections upon accepting them, simply replace
``close_upon_acceptance`` above with ``delay_before_sending_upon_acceptance --t=1 --length=1024``:

.. code-block:: console

   $ python -m poorconn delay_before_sending_upon_acceptance --t=1 --length=1024

Here, ``-H localhost -p 8000`` is omitted because it's Poorconn's default host and port settings. In this command,
:func:`poorconn.delay_before_sending_upon_acceptance` delays roughly 1 seconds for every 1024 bytes sent. The connection
is now throttled:

.. code-block:: console

   $ wget http://127.0.0.1:8000
   Connecting to 127.0.0.1:8000... connected.
   HTTP request sent, awaiting response... 200 OK
   Length: 1609 (1.6K) [text/html]
   Saving to: 'index.html'

   index.html    1.57K   804 B/s    in 2.0s  <====== NOTE the time

   'index.html' saved [1609/1609]

(Output above is abridged.)

Run ``python -m poorconn -h`` to view the help message and see the `poorconn module API references
<https://poorconn.topbug.net/apis/poorconn.html>`__ for a list of simulation functions (which share the same names with
simulation commands).

Docker Image
~~~~~~~~~~~~

You can also run Poorconn as a command line tool using our Docker image by replacing ``python -m poorconn`` with
``docker run poorconn``. For instance, the following achieves the same effect as the second example above:

.. code-block:: console

   $ docker run quay.io/xuhdev/poorconn delay_before_sending_upon_acceptance --t=1 --length=1024


Usage in Python
~~~~~~~~~~~~~~~

Running the following Python script achieves the same effects as the first command line example above:

.. code-block:: python

   from http.server import HTTPServer, SimpleHTTPRequestHandler
   from poorconn import close_upon_acceptance, make_socket_patchable

   # Start a local HTTP server that always closes connections upon established
   with HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler) as httpd:
       httpd.socket = make_socket_patchable(httpd.socket)
       close_upon_acceptance(httpd.socket)
       httpd.serve_forever()

The code snippet above is very similar to that runs a basic http server in Python, except that the socket object
``httpd.socket`` is patched by :func:`poorconn.close_upon_acceptance` before http server is running.

For the second command line example above, simply replace
``close_upon_acceptance(s)`` above with ``delay_before_sending_upon_acceptance(s, t=1, length=1024)`` and adjust
imports.

Integration with Pytest
~~~~~~~~~~~~~~~~~~~~~~~

If you use `pytest`_, you can also take advantage of poorconn fixtures in :mod:`poorconn.pytest_plugin`. The following
example gets you started with testing against a slow HTTP server:

.. code-block:: python

   pytest_plugins = ('poorconn',)

   from pathlib import Path
   import time
   import requests
   import pytest

   @pytest.mark.poorconn_http_server_config(t=2, length=1024)
   def test_slow_http_server(poorconn_http_server, tmp_path):
       "Test GETing from a slow local http server that delays 2 seconds to send every 1024 bytes."
       (tmp_path / 'index.txt').write_bytes(b'h' * 1024)
       starting_time = time.time()
       # Replace the following line with the program you want to test
       content = requests.get(f'{poorconn_http_server.url}/index.txt').content
       ending_time = time.time()
       assert ending_time - starting_time > 2

.. readme-misc

Bug Reports and Feature Requests
--------------------------------

Please open a ticket on the `GitLab Issue Tracker <https://gitlab.com/xuhdev/poorconn/-/issues>`__.

Contributing
------------

Contributions are welcome! To get started, check out :doc:`CONTRIBUTING`.

Copyright and License
---------------------

Unless otherwise stated in the headers of some files, all files in this project are licensed under LGPLv3+:

Copyright (C) 2020--2021 Hong Xu <hong@topbug.net>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along with this program. If not, see
<https://www.gnu.org/licenses/>.

.. _pytest: https://www.pytest.org
