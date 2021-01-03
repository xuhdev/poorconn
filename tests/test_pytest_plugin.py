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

from poorconn._pytest_plugin import _DEFAULT_PORT

pytest_plugins = ["pytester"]

minimum_test_file = dedent("""
    pytest_plugins = ("poorconn",)

    import time

    import pytest
    import requests

    {marks}
    def test_timeout(poorconn_http_server, tmp_path):
        (tmp_path / 'my.txt').write_bytes(b't' * 1024)
        starting_time = time.time()
        content = requests.get(f'{{poorconn_http_server.url}}/my.txt').content
        ending_time = time.time()
        assert content == b't' * 1024
        assert ending_time - starting_time > len(content) // 1024
        assert poorconn_http_server.server.server_port == {port}


    def test_timeout_2(poorconn_http_server, tmp_path):
        "A sanity check, in case something's broken if there's more than one test."
        (tmp_path / 'my.txt').write_bytes(b't' * 1024)
        starting_time = time.time()
        content = requests.get(f'{{poorconn_http_server.url}}/my.txt').content
        ending_time = time.time()
        assert content == b't' * 1024
        assert ending_time - starting_time > len(content) // 1024
""")


def test_poorconn_http_server(pytester):
    "Test fixture ``poorconn_http_server``."

    pytester.makepyfile(minimum_test_file.format(marks='', port=_DEFAULT_PORT))

    result = pytester.runpytest()

    result.assert_outcomes(passed=2)


def test_poorconn_http_server_config_port(pytester):
    "Test fixture ``poorconn_http_server`` when a non-default port is chosen."

    pytester.makepyfile(
        minimum_test_file.format(
            marks=f'@pytest.mark.poorconn_http_server_config(port={_DEFAULT_PORT + 300})',
            port=_DEFAULT_PORT + 300))

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_poorconn_http_server_config_invalid_port(pytester):
    "Test fixture ``poorconn_http_server`` when an invalid port is chosen."

    pytester.makepyfile(
        minimum_test_file.format(
            marks='@pytest.mark.poorconn_http_server_config(port=-1000)',
            port=-1000 + 100))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)


def test_poorconn_http_server_config_invalid_address(pytester):
    "Test fixture ``poorconn_http_server`` when an invalid address is chosen."

    pytester.makepyfile(
        minimum_test_file.format(
            marks='@pytest.mark.poorconn_http_server_config(address="example.com")',
            port=_DEFAULT_PORT))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)
