Command Line Usage
==================

Poorconn can be used from the command line. Both :ref:`quickstart` and ``python -m poorconn --help`` have offered some
introductory examples of the command line usage. The command line follows the following usage pattern:

.. code-block::

   python -m poorconn [-h] [-H HOST] [-p PORT] simulation_command ...

   optional arguments:
     -h, --help            show this help message and exit
     -H HOST, --host HOST  Host name to bind to (default: localhost)
     -p PORT, --port PORT  Port to bind to (default: 8000)

   Simulation commands:
     simulation_command
       close_upon_acceptance
                           Use poorconn.close_upon_acceptance
       delay_before_sending
                           Use poorconn.delay_before_sending
       delay_before_sending_once
                           Use poorconn.delay_before_sending_once
       delay_before_sending_upon_acceptance
                           Use poorconn.delay_before_sending_upon_acceptance
       delay_before_sending_upon_acceptance_once
                           Use poorconn.delay_before_sending_upon_acceptance_once

Here, ``simulation_command`` is one of the simulation functions listed in :doc:`../apis/poorconn`. The command hosts the
files in the current working directory as an HTTP server, and simulate the poor network condition as specified by
``simulation_command``.

How Does It Work?
~~~~~~~~~~~~~~~~~

The code above is effectively the same as running the following (pseudo-)Python script:

.. code-block:: python
   :linenos:

   from http.server import HTTPServer, SimpleHTTPRequestHandler
   import poorconn
   from poorconn import make_socket_patchable

   args = parse_arguments_from_command_line()

   with HTTPServer((args.host, args.port), SimpleHTTPRequestHandler) as httpd:
       httpd.socket = make_socket_patchable(httpd.socket)
       simulation_func = getattr(poorconn, args.simulation_command)
       simulation_func(httpd.socket, **args.simulation_command_parameters)
       httpd.serve_forever()

:doc:`main` explains the usage from within Python in detail.
