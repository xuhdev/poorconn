# Copyright (C) 2020  Hong Xu <hong@topbug.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from contextlib import contextmanager
from socket import socket

from http.server import HTTPServer
import threading


@contextmanager
def mirror_server_socket_new_thread(sock: socket):
    "Start a server socket in a new thread that accepts a connection, and then sends back whatever it receives."
    stop = False

    def server_socket_work():
        sock.listen()
        conn, addr = sock.accept()
        while not stop:
            data = conn.recv(1024)
            conn.sendall(data)

    thread = threading.Thread(target=server_socket_work, name='Mirror socket server', daemon=True)
    thread.start()
    thread.join(timeout=1)
    yield thread
    stop = True
    thread.join()


def httpd_serve_new_thread(httpd: HTTPServer) -> threading.Thread:
    "Let an ``HTTPServer`` object start serve on a new thread."

    thread = threading.Thread(target=httpd.serve_forever, name='Http server on a new thread', daemon=True)
    thread.start()
    thread.join(timeout=1)  # Wait a bit to ensure the server starts up
    return thread
