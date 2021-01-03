Welcome to Poorconn's Documentation!
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Poorconn simulates unstable network conditions. It is suitable for testing purposes. Install this package via

.. code-block:: console

   pip install poorconn

If you use :mod:`pytest`:

.. code-block:: python

   pytest_plugins = ('poorconn',)

   from pathlib import Path
   import time
   import requests

   def test_slow_http_server(poorconn_http_server):
       "Test on a slow http server."
       (tmp_path / 'index.txt').write_text('Hello, poorconn!')
       starting_time = time.time()
       content = requests.get(f'{poorconn_http_server.url}/index.txt').content
       ending_time = time.time()
       assert ending_time - starting_time > 1

API References
==============

.. autosummary::
   :toctree: apis
   :template: poorconn-module.rst

   poorconn
   poorconn.pytest_plugin

Indices and Tables
==================

* :ref:`genindex`
* :ref:`search`
