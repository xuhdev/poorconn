Poorconn: Simulating Unstable Network Conditions
================================================

Poorconn simulates unstable network conditions. It is suitable for testing purposes.

Quickstart
----------

Install this package via

.. code-block:: console

   $ pip install 'poorconn[full]'  # or "pip install poorconn" if you don't need pytest support

If you use `pytest`_, the following example gets you started with testing against a slow HTTP server:

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

If you don't use `pytest`_ (or need advanced features that pytest fixtures do not provide), the following example starts
a local HTTP server at port 8000 that always closes connections upon accepting them:

.. code-block:: python

   from http.server import HTTPServer, SimpleHTTPRequestHandler
   from poorconn import close_upon_accepting, make_socket_patchable

   # Start a local HTTP server that always closes connections upon established
   with HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler) as httpd:
       httpd.socket = make_socket_patchable(httpd.socket)
       close_upon_accepting(httpd.socket)
       httpd.serve_forever()

After running the code above, connections from a client would establish but fail to communicate subsequently:

.. code-block:: console

   $ wget -t 1 http://127.0.0.1:8000
   Connecting to 127.0.0.1:8000... connected.
   HTTP request sent, awaiting response... No data received.
   Giving up.

.. readme-roles

.. role:: doc(literal)

.. readme-misc

Bug Reports and Feature Requests
--------------------------------

Please open a ticket on the `GitLab Issue Tracker <https://gitlab.com/xuhdev/poorconn/-/issues>`__.

Contributing
------------

Contributions are welcome! To get started, check out :doc:`CONTRIBUTING`.

Copyright and License
---------------------

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
