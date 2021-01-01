# Copyright (C) 2021  Hong Xu <hong@topbug.net>

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

from textwrap import dedent


def test_poorconn_http_server(pytester):
    "Test fixture poorconn_http_server."

    txt_file = pytester.maketxtfile('1024')

    txt_file.write_bytes(b't' * 1024)

    pytester.makepyfile(
        f"txt_file = '{txt_file.name}'" +
        dedent("""
        pytest_plugins = ("poorconn",)

        import time

        import requests


        def test_timeout(poorconn_http_server, poorconn_http_url):
            starting_time = time.time()
            content = requests.get(f'{poorconn_http_url}/{txt_file}').content
            ending_time = time.time()
            assert content == b't' * 1024
            assert ending_time - starting_time > len(content) // 1024
        """))

    result = pytester.runpytest()

    result.assert_outcomes(passed=1)
