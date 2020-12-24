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

from socket import socket
import time
from types import BuiltinMethodType
from typing import Any, Callable

from ._wrappers import wrap, wrap_accept, wrap_send

from ._socket import PatchableSocket


def delay_before_sending_once(s: socket, t: float):
    """Delay ``t`` seconds before sending for once (first time only).

    :param s: The :class`socket.socket` object whose sending methods are to be delayed for once and once only.
    :param t: Number of seconds to delay.
    """

    class DelayOnce():
        def __init__(self, t: float):
            self.t: float = t
            self._first_time: bool = True

        def __call__(self, *args: Any, **kwargs: Any):
            if self._first_time:
                time.sleep(t)
                self._first_time = False

    wrap_send(s, before=DelayOnce(t))


def delay_before_sending(s: socket, t: float, length: int = 1024) -> None:
    """Chop the content (``bytes`` in :meth:`socket.socket.send` and :meth:`socket.socket.sendall`) to be sent in
    ``length`` bytes and delay ``t`` seconds before sending every time.

    :param s: The :class:`socket.socket` object whose sending methods are to be delayed every time.
    :param t: Number of seconds to delay.
    :param length: Number of bytes of each of the slices into which the content is chopped.
    """

    class DelaySendEveryTime:
        def __init__(self, t: float, length: int):
            self.t: float = t
            self.length: int = length

        def __call__(self, sock: socket, *args: Any, **kwargs: Any):
            bytes_ = args[0] if len(args) > 0 else kwargs.get('bytes')  # Content of the bytes parameter from send
            time.sleep(t)
            return (bytes_[:min(length, len(bytes_))],), {}

    # For send, simply truncate the length of the content to be sent to ``length`` and delay that by ``t`` seconds.
    wrap(s, meth='send', before=DelaySendEveryTime(t, length), before_pass=True)
    # TODO: Wrap sendall properly here


def wrap_sending_upon_acceptance(s: socket, wrapper: Callable, *args: Any, **kwargs: Any):
    """Wrap sending functions of the connection socket returned by ``s.accept()``.
    :param s: The :class:`socket.socket` object where ``s.accept()``'s sending methods are to be wrapped.
    :param wrapper: The wrapper function.
    :param args: Positional parameters to be passed to the wrapper.
    :param kwargs: Keyword parameters to be passed to the wrapper.
    """

    def after(s, *, original, before):
        conn_sock = original[0]
        if isinstance(conn_sock.send, BuiltinMethodType) or \
           isinstance(conn_sock.sendall, BuiltinMethodType):  # conn_sock.send or conn_sock.sendall are not modifiable
            conn_sock = PatchableSocket.create_from(conn_sock)
        wrapper(conn_sock, *args, **kwargs)
        return conn_sock, original[1]

    wrap_accept(s, after=after)


def delay_before_sending_upon_acceptance_once(s: socket, t: float):
    """Delay ``t`` seconds before sending for all sockets returned by ``s.accept()``, for once (first time only).
    Parameters mean the same as :func:`.delay_before_sending`.
    """

    wrap_sending_upon_acceptance(s, delay_before_sending_once, t=t)
