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
from ssl import SSLContext, SSLSocket

from poorconn import make_socket_patchable, PatchableSocket


def test_make_socket_patchable():
    "Test ``make_socket_patchable``."

    s = make_socket_patchable(socket())
    assert isinstance(s, PatchableSocket)

    s = make_socket_patchable(SSLContext().wrap_socket(socket()))
    assert isinstance(s, SSLSocket)
    assert not isinstance(s, PatchableSocket)
