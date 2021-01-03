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

from __future__ import annotations

from socket import socket
import threading
from typing import Any, Iterable, no_type_check


class PatchableSocket(socket):
    """A class that allows some :class:`socket.socket` functions to be patchable and thus can be wrapped.

    Many functions such as :meth:`socket.socket.accept` cannot be patched because it is builtin.
    """

    @classmethod
    def create_from(cls, s: socket) -> PatchableSocket:
        """Create a :class:`PatchableSocket` object from ``s``.

        :param s: The :class:`socket.socket` object to be created from.
        """

        # This part is partly based on the builtin ssl.py
        # Detach all underlying objects and reconstruct the socket object.
        kwargs = {'family': s.family, 'type': s.type, 'proto': s.proto, 'fileno': s.fileno()}
        timeout = s.gettimeout()
        s.detach()

        patchable_sock = cls(**kwargs)
        patchable_sock.settimeout(timeout)

        return patchable_sock

    @no_type_check
    def accept(self, *args, **kwargs):
        "Wraps :meth:`~socket.socket.accept` so that this function is patchable."
        return super().accept(*args, **kwargs)

    @no_type_check
    def send(self, *args, **kwargs):
        "Wraps :meth:`~socket.socket.send` so that this function is patchable."
        return super().send(*args, **kwargs)

    @no_type_check
    def sendall(self, *args, **kwargs):
        "Wraps :meth:`~socket.socket.sendall` so that this function is patchable."
        return super().sendall(*args, **kwargs)


_patchability_thread_lock: threading.Lock = threading.Lock()


def is_patchable(s: Any, attr: str) -> bool:
    """Test whether ``s.attr`` is patchable.

    :param s: The object.
    :param attr: The name of the attribute.
    :return: True if ``s.attr`` is patchable, False otherwise.
    """
    with _patchability_thread_lock:
        cur_attr = getattr(s, attr)
        try:
            setattr(s, attr, 1)
        except AttributeError:  # readonly attribute
            return False
        else:
            setattr(s, attr, cur_attr)
            return True


def make_socket_patchable(s: socket, funcs: Iterable[str] = (':sending', 'accept')) -> socket:
    """Make a socket patchable: Create a :class:`.PatchableSocket` object if any functions in ``funcs`` are not
    patchable. This function is not thread-safe even if ``s`` is returned. Please ensure that no other threads are
    operating on ``s`` during the execution of this function.

    :param s: The socket to be made patchable.
    :param funcs: Create a :class:`.PatchableSocket` object if any functions in it are not patchable. ``':sending'``
        means ``'send'`` and ``'sendall'``, and may include any additional sending methods in the future.
    """

    for func in funcs:
        if func == ':sending':
            fs: Iterable[str] = ('send', 'sendall')
        else:
            fs = (func,)

        if not any(is_patchable(s, f) for f in fs):
            return PatchableSocket.create_from(s)

    return s
