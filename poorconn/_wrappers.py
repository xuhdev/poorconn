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
from types import MethodType
from typing import Any, Callable, Optional


def wrap(s: socket, *,
         meth: str,
         before: Optional[Callable[..., Any]] = None,
         before_pass: bool = False,
         after: Optional[Callable[..., Any]] = None) -> None:
    """Wrap a socket member method named ``meth``.

    :param s: The socket object.
    :param meth: Name of the method to be wrapped.
    :param before: Function to be called before :func:`socket.socket.accept`. The socket object will be passed in as the
        first parameter.
    :param before_pass: If True, ``before`` should return a tuple of size 2 with an interable and a dictionary, which is
        then passed to the wrapped method as positional arguments and keyword arguments instead of the arguments
        originally passed in by the called.
    :param after: Function to be called after :func:`socket.socket.accept`. The socket object will be passed in as the
        first parameter. It must accept a ``wrapped`` keyword argument, to which the return value of the wrapped
        :func:`socket.socket.accept` will be passed. It must accept a ``before`` keyword argument, to which the return
        value of the ``before`` function will be pass.
    """

    wrapped_meth = getattr(s, meth)

    def wrapping_function(self: socket, *args: Any, **kwargs: Any) -> Any:
        ret_before = before(self, *args, **kwargs) if before is not None else None
        if before_pass:
            ret_wrapped = wrapped_meth(*ret_before[0], **ret_before[1])
        else:
            ret_wrapped = wrapped_meth(*args, **kwargs)
        return after(self, original=ret_wrapped, before=ret_before) if after is not None else ret_wrapped

    setattr(s, meth, MethodType(wrapping_function, s))


def wrap_accept(s: socket, *,
                before: Optional[Callable[..., Any]] = None,
                after: Optional[Callable[..., Any]] = None) -> None:
    "Wrap :meth:`socket.socket.accept`. This function calls :func:`.wrap` with ``meth='accept'``."

    wrap(s, meth='accept', before=before, after=after)


def wrap_send(s: socket, *,
              before: Optional[Callable[..., Any]] = None,
              after: Optional[Callable[..., Any]] = None,
              before_pass: bool = False) -> None:
    """Wrap :meth:`socket.socket.send`, :meth:`socket.socket.sendall`. This function calls :func:`.wrap` twice with
    ``meth='send'`` and ``meth='sendall'``.
    """

    for meth in ('send', 'sendall'):
        wrap(s, meth=meth, before=before, after=after, before_pass=before_pass)
