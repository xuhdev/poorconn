Contributing Guide
------------------

Development
~~~~~~~~~~~

Set up Development Environment
++++++++++++++++++++++++++++++

To start developing, install `tox`_ and let it configure the development environment:

.. code-block:: console

    $ pip install tox
    $ tox -e dev
    $ . .tox/dev/bin/activate

Or, if you have set up your own environment, you can install all development dependencies by running:

.. code-block:: console

    $ pip install -r requirements-dev.txt

Run Tests
+++++++++

To run lint, run:

.. code-block:: console

    $ tox -e lint

To run tests, run:

.. code-block:: console

    $ tox -e py37  # or py38, py39, whichever you are using

To generate documentation to :file:`.tox/docs/_build/html`, run:

.. code-block:: console

    $ tox -e docs

Submit Your Contributions
~~~~~~~~~~~~~~~~~~~~~~~~~

To submit your contributions, open a `merge request`_ on `our gitlab repository
<https://gitlab.com/xuhdev/poorconn/-/merge_requests>`__.

.. _merge request: https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html
.. _tox: https://tox.readthedocs.io/en/latest/
