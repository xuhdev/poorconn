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

"The command line interface of Poorconn."


from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, RawDescriptionHelpFormatter
from http.server import HTTPServer, SimpleHTTPRequestHandler
import shlex
import sys
import textwrap
from typing import Callable, Dict, List, NamedTuple, Sequence

import poorconn
from poorconn import make_socket_patchable

shell_join = shlex.join if sys.version_info >= (3, 8) else ' '.join


class ArgumentFormatter(ArgumentDefaultsHelpFormatter, RawDescriptionHelpFormatter):
    "The formatter for our argument parsing."
    pass


SimulationCommand = NamedTuple('SimulationCommand', [('name', str),
                                                     ('params', Dict[str, Callable])])

simulation_commands: List[SimulationCommand] = [
    SimulationCommand('close_upon_acceptance', {}),
    SimulationCommand('delay_before_sending', {'t': float, 'length': int}),
    SimulationCommand('delay_before_sending_once', {'t': float}),
    SimulationCommand('delay_before_sending_upon_acceptance', {'t': float, 'length': int}),
    SimulationCommand('delay_before_sending_upon_acceptance_once', {'t': float})]
"""Each simulation command corresponds to the function with the same name under :mod:`poorconn`. The dictionary lists
the type conversion function for each parameter from the command line arguments. This does not necessarily overlap with
the type annotation of the underlying simulation function, because they may accept multiple types but we can only
convert them to one type from the command line argument."""


def update_arg_parser_from_simulation_function(s: SimulationCommand, arg_parser: ArgumentParser) -> None:
    """Add arguments to an :class:`argparser.ArgumentParser` object according to the underlying simulation function of a
    simulation command.

    :param s: The :class:`.SimulationCommand` object that represent the simulation command.
    :param arg_parser: The :class:`argparser.ArgumentParser` object that corresponds to the simulation function ``s``.
    """

    simulation_function = getattr(poorconn, s.name)

    defaults = () if simulation_function.__defaults__ is None else simulation_function.__defaults__
    param_list = simulation_function.__code__.co_varnames[:simulation_function.__code__.co_argcount]
    num_required_param = len(param_list) - len(defaults)
    for i, param in enumerate(param_list):
        if param == 's':
            continue
        required = (i < num_required_param)
        default = None if required else defaults[i - num_required_param]
        arg_parser.add_argument(f'--{param}',
                                help=f'The value to pass to the keyword argument "{param}" of "poorconn.{s}"',
                                dest=f'{s.name}_param_{param}',
                                required=required,
                                default=default,
                                type=s.params[param])


def main(argv: Sequence) -> None:
    """Command line entrypoint.

    :param argv: Command line arguments.
    """

    arg_parser = ArgumentParser(
        prog=shell_join((sys.executable, '-m', vars(sys.modules[__name__])['__package__'])),
        formatter_class=ArgumentFormatter,
        epilog=textwrap.dedent('''
        Example:

        Start a HTTP server at localhost port 9000 that hosts static files at the current working directory. Require the
        HTTP server to always closes connections upon accepting them:

            %(prog)s -H localhost -p 9000 close_upon_acceptance

        Start a HTTP server at localhost port 8000 that hosts static files at the current working directory. Throttle
        the speed to roughly 1 KiB per second:

            %(prog)s -m poorconn delay_before_sending_upon_acceptance --t=1 --length=1024
        '''))
    arg_parser.add_argument('-H', '--host', help='Host name to bind to', type=str, default='localhost')
    arg_parser.add_argument('-p', '--port', help='Port to bind to', type=int, default=8000)

    subparsers = arg_parser.add_subparsers(title='Simulation commands', metavar='simulation_command',
                                           dest='simulation_command')
    for simulation_command in simulation_commands:
        subparser = subparsers.add_parser(simulation_command.name, help=f'Use poorconn.{simulation_command.name}',
                                          formatter_class=ArgumentDefaultsHelpFormatter)
        update_arg_parser_from_simulation_function(simulation_command, subparser)

    if len(argv) == 0:
        arg_parser.print_help(sys.stderr)
        sys.exit(1)

    args = arg_parser.parse_args(argv)

    with HTTPServer((args.host, args.port), SimpleHTTPRequestHandler) as httpd:
        httpd.socket = make_socket_patchable(httpd.socket)
        simulation_func = getattr(poorconn, args.simulation_command)
        simulation_func(httpd.socket,
                        **{arg_name[len(f'{args.simulation_command}_param_'):]: arg_val
                           for arg_name, arg_val in vars(args).items()
                           if arg_name.startswith(f'{args.simulation_command}_param_')})
        httpd.serve_forever()
