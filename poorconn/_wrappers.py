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
from types import MethodType
from typing import Any, Callable, Optional


def wrap(s: socket, *,
         meth: str,
         before: Optional[Callable[[socket], Any]] = None,
         after: Optional[Callable[..., Any]] = None) -> None:
    """Wrap a socket member method named ``meth``.

    :param s: The socket object.
    :param meth: Name of the method to be wrapped.
    :param before: Function to be called before :func:`socket.socket.accept`. The socket object will be passed in as the
    first parameter.
    :param after: Function to be called after :func:`socket.socket.accept`. The socket object will be passed in as the
        first parameter. It must accept a ``wrapped`` keyword argument, to which the return value of the wrapped
        :func:`socket.socket.accept` will be passed. It must accept a ``before`` keyword argument, to which the return
        value of the ``before`` function will be pass.
    """

    wrapped_meth = getattr(s, meth)

    def wrapping_function(self, *args: Any, **kwargs: Any) -> Any:
        ret_before = before(self) if before is not None else None
        ret_wrapped = wrapped_meth(*args, **kwargs)
        return after(self, original=ret_wrapped, before=ret_before) if after is not None else ret_wrapped

    setattr(s, meth, MethodType(wrapping_function, s))  # type: ignore


def wrap_accept(s: socket, *,
                before: Optional[Callable[[socket], Any]] = None,
                after: Optional[Callable[..., Any]] = None) -> None:
    "Wrap :meth:`socket.socket.accept`. This function calls :func:`.wrap` with ``meth='accept'``."

    wrap(s, meth='accept', before=before, after=after)
