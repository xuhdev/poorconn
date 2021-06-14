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

from socket import socket, SHUT_RDWR
from typing import Any, Sequence

from ._wrappers import wrap_accept


def close_upon_acceptance(s: socket) -> None:
    """Shutdown and close the connection socket upon accepting.

    :param s: The :class:`socket.socket` object whose ``accept()`` function is to be wrapped.

    .. versionchanged:: 0.2
       Renamed from ``close_upon_accepting``.
    """

    def after(s: socket, *, original: Sequence, before: Any) -> Any:
        original[0].shutdown(SHUT_RDWR)
        original[0].close()
        return original

    wrap_accept(s, after=after)
