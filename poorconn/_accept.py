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

from ._wrappers import wrap_accept


def close_upon_accepting(s: socket):
    """Close the socket upon accepting.

    :param s: The :class`socket.socket` object whose ``accept()`` function is to be wrapped.
    """

    def after(s, *, original, before):
        s.close()

    return wrap_accept(s, after=after)
