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
from typing import Any

import pytest

from poorconn.pytest_plugin._impl import _PoorConnHTTPServerDefault

pytest_plugins = ["pytester"]

_DEFAULT_PORT = _PoorConnHTTPServerDefault.PORT

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
        assert ending_time - starting_time > ((len(content) // {length}) + (len(content) % {length})) * {t}
        assert poorconn_http_server.server.server_port == {port}


    def test_timeout_2(poorconn_http_server, tmp_path):
        "A sanity check, in case something's broken if there's more than one test."
        (tmp_path / 'my.txt').write_bytes(b't' * 1024)
        starting_time = time.time()
        content = requests.get(f'{{poorconn_http_server.url}}/my.txt').content
        ending_time = time.time()
        assert content == b't' * 1024
        assert ending_time - starting_time > ((len(content) // {length}) + (len(content) % {length})) * {t}
""")

minimum_test_file_default_args = {
    'marks': '',
    'port': _DEFAULT_PORT,
    'length': _PoorConnHTTPServerDefault.LENGTH,
    't': _PoorConnHTTPServerDefault.T,
}


def _merge_default_args(**kwargs: Any) -> dict:
    "Merge ``minimum_test_file_default_args`` to ``kwargs``."
    params = minimum_test_file_default_args.copy()
    params.update(kwargs)
    return params


def _format_with_default_args(s: str, **kwargs: Any) -> str:
    "Format with missing args from ``minimum_test_file_default_args``."
    return s.format(**_merge_default_args(**kwargs))


def test_poorconn_http_server(pytester):
    "Test fixture ``poorconn_http_server``."

    pytester.makepyfile(_format_with_default_args(minimum_test_file))

    result = pytester.runpytest()

    result.assert_outcomes(passed=2)


def test_poorconn_http_server_config_port(pytester):
    "Test fixture ``poorconn_http_server`` when a non-default port is chosen."

    pytester.makepyfile(
        _format_with_default_args(
            minimum_test_file,
            marks=f'@pytest.mark.poorconn_http_server_config(port={_DEFAULT_PORT + 300})',
            port=_DEFAULT_PORT + 300))

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_poorconn_http_server_config_invalid_port(pytester):
    "Test fixture ``poorconn_http_server`` when an invalid port is chosen."

    pytester.makepyfile(
        _format_with_default_args(
            minimum_test_file,
            marks='@pytest.mark.poorconn_http_server_config(port=-1000)',
            port=-1000))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)


def test_poorconn_http_server_config_invalid_address(pytester):
    "Test fixture ``poorconn_http_server`` when an invalid address is chosen."

    pytester.makepyfile(
        _format_with_default_args(
            minimum_test_file,
            marks='@pytest.mark.poorconn_http_server_config(address="example.com")'))

    result = pytester.runpytest()
    result.assert_outcomes(passed=1, errors=1)


@pytest.mark.parametrize('t,length',
                         [(1.3, 300),
                          (1.1, 512),
                          (2.1, 789),
                          # (1, 1024),  # The default, which has been tested in test_poorconn_http_server
                          (2, 1870),
                          (1, 2048)])
def test_poorconn_http_server_config_delay(pytester, t, length):
    "Test fixture ``poorconn_http_server`` with different delays."

    pytester.makepyfile(
        _format_with_default_args(
            minimum_test_file,
            marks=f'@pytest.mark.poorconn_http_server_config(t={t}, length={length})'))

    result = pytester.runpytest()
    result.assert_outcomes(passed=2)


def test_poorconn_http_server_config_delay_parametrized(pytester):
    "Test fixture ``poorconn_http_server`` with different delays, along with parametrizing."

    pytester.makepyfile(
        _format_with_default_args(
            minimum_test_file,
            marks=(dedent('''
            @pytest.mark.parametrize("", [
                 pytest.param(marks=pytest.mark.poorconn_http_server_config(t=1.4, length=400)),
                 pytest.param(marks=pytest.mark.poorconn_http_server_config(t=1.9, length=1212)),
            ])'''))))

    result = pytester.runpytest()
    result.assert_outcomes(passed=3)
