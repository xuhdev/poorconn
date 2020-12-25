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


from types import BuiltinMethodType
from typing import Iterable
from socket import socket


class PatchableSocket(socket):
    """A class that allows some :class:`socket.socket` functions to be patchable and thus can be wrapped.

    Many functions such as :meth:`socket.socket.accept` cannot be patched because it is builtin.
    """

    @classmethod
    def create_from(cls, s: socket) -> 'PatchableSocket':
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

    def accept(self, *args, **kwargs):
        "Wraps :meth:`socket.socket.accept` so this function is patchable."
        return super().accept(*args, **kwargs)

    def send(self, *args, **kwargs):
        "Wraps :meth:`socket.socket.send` so this function is patchable."
        return super().send(*args, **kwargs)

    def sendall(self, *args, **kwargs):
        "Wraps :meth:`socket.socket.sendall` so this function is patchable."
        return super().sendall(*args, **kwargs)


def make_socket_patchable(s: socket, funcs: Iterable[str] = (':sending', 'accept')) -> socket:
    """Make a socket patchable: Create a :class:`.PatchableSocket` object if any functions in ``funcs`` are not
    patchable.

    :param s: The socket to be made patchable.
    :param funcs: Create a :class:`.PatchableSocket` object if any functions in it are not patchable. ``':sending'``
        means ``'send'`` and ``'sendall'``, and may include any additional sending methods in the future.
    """

    for func in funcs:
        if func == ':sending':
            fs: Iterable[str] = ('send', 'sendall')
        else:
            fs = (func,)

        for f in fs:
            if isinstance(getattr(s, f), BuiltinMethodType):
                return PatchableSocket.create_from(s)

    return s
