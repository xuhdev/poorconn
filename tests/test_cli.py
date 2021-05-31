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

import itertools
import pathlib
import subprocess
import sys
import threading
import time

import pytest
import requests

from poorconn._cli import main


def run_from_cli(argv):
    "Run from the command line interface."

    return subprocess.run((sys.executable, '-m', 'poorconn') + tuple(argv), capture_output=True, text=True)


def test_empty(capsys):
    'Test when no option is passed in (``python -m poorconn``).'

    with pytest.raises(SystemExit) as e:
        main([])

    assert e.value.code == 1
    out, err = capsys.readouterr()
    assert 'Simulation commands' in err
    assert 'close_upon_acceptance' in err
    assert 'Example' in err
    assert len(out) == 0

    # A little sanity test to make sure the program work from the actual command line interface
    cmd = run_from_cli([])
    assert cmd.returncode == 1
    assert 'Simulation commands' in cmd.stderr
    assert 'close_upon_acceptance' in cmd.stderr
    assert 'Example' in cmd.stderr
    assert len(cmd.stdout) == 0


@pytest.mark.parametrize('help_op', ("-h", "--help"))
def test_help(capsys, help_op):
    'Test help options.'

    with pytest.raises(SystemExit) as e:
        main([help_op])

    assert e.value.code == 0
    out, err = capsys.readouterr()
    assert 'Simulation commands' in out
    assert 'close_upon_acceptance' in out
    assert 'Example' in out
    assert len(err) == 0

    # A little sanity test to make sure the program work from the actual command line interface
    cmd = run_from_cli([help_op])
    assert cmd.returncode == 0
    assert 'Simulation commands' in cmd.stdout
    assert 'close_upon_acceptance' in cmd.stdout
    assert 'Example' in cmd.stdout
    assert len(cmd.stderr) == 0


@pytest.mark.parametrize('help_op',
                         tuple(itertools.product(["delay_before_sending_once", "delay_before_sending_upon_acceptance"],
                                                 ["-h", "--help"])))
def test_simulation_command_help(capsys, help_op):
    'Test help options for simulation commands.'

    with pytest.raises(SystemExit) as e:
        main(help_op)

    assert e.value.code == 0
    out, err = capsys.readouterr()
    assert '--t' in out
    assert len(err) == 0

    # A little sanity test to make sure the program work from the actual command line interface
    cmd = run_from_cli(help_op)
    assert cmd.returncode == 0
    assert '--t' in cmd.stdout
    assert len(cmd.stderr) == 0


def test_basic_usage():
    "test the basic usage of the command line."

    # There's no graceful way to kill the thread. We set daemon=True and let it be killed until the end of the test
    # session.
    thread = threading.Thread(target=lambda: main(['-p', '10009', '-H', 'localhost',
                                                   'delay_before_sending_upon_acceptance', '--t', '1']),
                              name='Command line thread', daemon=True)
    thread.start()

    time.sleep(2)  # Wait for the HTTP server to startup
    response = requests.get('http://localhost:10009/setup.py', timeout=2)
    assert response.status_code == 200
    assert response.content == pathlib.Path('./setup.py').read_bytes()
