Tutorial
========

.. currentmodule:: poorconn

Poorconn is a Python package that simulates poor network conditions. If you have not done so, it is recommended to read
:ref:`quickstart` first to have an overall feel about poorconn usage.

Poorconn consists of two parts:

- The main package :mod:`poorconn` that provides generically useful functions that can be used in any Python code, and
- the subpackage :mod:`poorconn.pytest_plugin` that provides useful `pytest`_ utilities.

The Main Package :mod:`poorconn`
--------------------------------

Basic Usage
~~~~~~~~~~~

The main package :mod:`poorconn` includes a list of simulation functions that modify a :class:`~socket.socket` object so
that it behaves poorly as if it were under poor network conditions. To use one of these simulation functions, always
ensure that the :class:`~socket.socket` object is patchable (so that it can be modified, will be explained in
:ref:`how-does-it-work` below) by calling :func:`make_socket_patchable` first, then call the simulation function that
you would like to use.

For example, consider :func:`delay_before_sending`, a simulation function that delays a :class:`~socket.socket` object
every time when it tries to send a message. The following code snippet achieves this effect on the
:class:`~socket.socket` object ``s``:

.. code-block:: python
   :linenos:

   from socket import socket
   from poorconn import delay_before_sending, make_socket_patchable

   s = socket()
   s = make_socket_patchable(s)
   delay_before_sending(s, 2, 1024)

The code snippet above turns ``s`` to delay 2 seconds for sending every 1024 bytes of messages. Line 5 calls
:func:`make_socket_patchable` so that ``s`` becomes patchable (so that it can be modified, will be explained in
:ref:`how-does-it-work` below). Line 6 calls :func:`delay_before_sending` so that ``s``'s sending methods are patched so
that extra code that delays the sending is in place. As the example in :ref:`quickstart` shows, simulation functions can
also be applied to socket objects that are used in HTTP server objects.

.. _how-does-it-work:

How Does It Work?
~~~~~~~~~~~~~~~~~

The main package simulates poor network conditions by `monkey patching
<https://stackoverflow.com/questions/5626193/what-is-monkey-patching>`__ ("patching" for short) methods in
:class:`~socket.socket`. It wraps the original :class:`~socket.socket` methods with code that simulates the intended
effects. For example, :func:`delay_before_sending` replaces :meth:`~socket.socket.send` and
:meth:`~socket.socket.sendall` with a different implementation. This implementation chops the message into certain
number of bytes (1024 in the example above), delays a certain amount of time (2 seconds in the example above), and then
calls the original :meth:`~socket.socket.send`/:meth:`~socket.socket.sendall` function.

However, not every :class:`~socket.socket` object can be patched by default. For example, if you use `CPython`_,
:meth:`socket.socket.send` is not patchable:

.. code-block:: python

   >>> from socket import socket
   >>> s = socket()
   >>> s.send = lambda: None
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
   AttributeError: 'socket' object attribute 'send' is read-only

This is why we provide :func:`make_socket_patchable`. This function first detects whether pertinent methods (such as
:meth:`~socket.socket.send`) of an object are patchable. If yes, it does nothing and returns the object. If not, it
would detach the underlying C socket object and attach it to a newly created :class:`PatchableSocket` object. A
:class:`PatchableSocket` object is almost the same as a :class:`socket.socket` object, except that all pertinent methods
are made patchable. Therefore, it is recommended to always call :func:`make_socket_patchable` before calling any
simulation functions.

Advanced Usage
~~~~~~~~~~~~~~

Stacking Simulation Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Thanks to the mechanism in :ref:`how-does-it-work`, it is possible to stack simulation functions with other functions.
For example, to create an HTTPS server that always accepts incoming connections but immediately closes the connection,
simply apply a simulation function after applying an SSL wrapper:

.. literalinclude:: ./examples/https.py
   :caption: https.py
   :language: python
   :linenos:

(Download :download:`https.py <./examples/https.py>`)

After running this script, connections from a client would establish but fail to communicate subsequently:

.. code-block:: console

   $ wget --no-check-certificate -t 1 https://localhost:8888
   Resolving localhost (localhost)... ::1, 127.0.0.1
   Connecting to localhost (localhost)|::1|:8888... failed: Connection refused.
   Connecting to localhost (localhost)|127.0.0.1|:8888... connected.
   WARNING: The certificate of ‘localhost’ is not trusted.
   WARNING: The certificate of ‘localhost’ doesn't have a known issuer.
   HTTP request sent, awaiting response... Read error (Success.) in headers.
   Giving up.
