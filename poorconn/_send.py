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
import time
from types import MethodType
from typing import Any, Callable, Dict, Sequence, Tuple

from ._wrappers import wrap, wrap_accept, wrap_send

from ._socket import make_socket_patchable


class DelayBeforeSendingOnceController:
    """Controller for :func:`.delay_before_sending_once`. Objects are always created and returned by
    :func:`.delay_before_sending_once` and should not be created outside the :mod:`poorconn` package.

    :param t: Same as ``t`` in :func:`delay_before_sending_once`.
    """

    __slots__ = (
        't',
        '_first_time'
    )

    def __init__(self, t: float):
        super().__init__()
        self.t: float = t
        """Same as ``t`` in :func:`delay_before_sending_once`. Updating it in the controller affects ``s`` in
        :func:`delay_before_sending_once`."""
        self._first_time = True

    def reset(self) -> None:
        "Reset delay."
        self._first_time = True

    def _use(self) -> bool:
        """Used internally to signal that delaying should start.

        :return: True if delay is ready to start. False if delay has been started before and :meth:`.reset` has never
        been called.
        """
        if self._first_time:
            self._first_time = False
            return True
        else:
            return False


def delay_before_sending_once(s: socket, t: float) -> DelayBeforeSendingOnceController:
    """Delay ``t`` seconds before sending for once (first time only).

    :param s: The :class:`socket.socket` object whose sending methods are to be delayed for once and once only.
    :param t: Number of seconds to delay.

    :return: A :class:`DelayBeforeSendingOnceController` object that controls the patched socket object.
    """

    controller = DelayBeforeSendingOnceController(t)

    class DelayOnce():
        def __init__(self, controller: DelayBeforeSendingOnceController):
            self._controller: DelayBeforeSendingOnceController = controller

        def __call__(self, *args: Any, **kwargs: Any) -> None:
            if self._controller._use():
                time.sleep(t)

    wrap_send(s, before=DelayOnce(controller))

    return controller


class DelayBeforeSendingController:
    """Controller for :func:`.delay_before_sending`. Objects are always created and returned by
    :func:`.delay_before_sending` and should not be created outside the :mod:`poorconn` package.

    :param t: Same as ``t`` in :func:`delay_before_sending`.
    :param length: Same as ``length`` in :func:`delay_before_sending`.
    """

    __slots__ = (
        't',
        'length',
    )

    def __init__(self, t: float, length: int):
        super().__init__()
        self.t: float = t
        """Same as ``t`` in :func:`delay_before_sending`. Updating it in the controller affects ``s`` in
        :func:`delay_before_sending`."""
        self.length: int = length
        """Same as ``length`` in :func:`delay_before_sending`. Updating it in the controller affects ``s`` in
        :func:`delay_before_sending`."""


def delay_before_sending(s: socket, t: float, length: int = 1024) -> DelayBeforeSendingController:
    """Chop the content (``bytes`` in :meth:`socket.socket.send` and :meth:`socket.socket.sendall`) to be sent in
    ``length`` bytes and delay ``t`` seconds before sending every time.

    :param s: The :class:`socket.socket` object whose sending methods are to be delayed every time.
    :param t: Number of seconds to delay.
    :param length: Number of bytes of each of the slices into which the content is chopped.

    :return: A :class:`DelayBeforeSendingController` object that controls the patched socket object.
    """

    controller = DelayBeforeSendingController(t=t, length=length)

    def before(sock: socket, *args: Any, **kwargs: Any) -> Tuple[Tuple, Dict]:
        time.sleep(controller.t)
        bytes_ = args[0] if len(args) > 0 else kwargs.get('bytes')  # Content of the bytes parameter from send
        flags = args[1] if len(args) > 1 else kwargs.get('flags')
        return (bytes_[:min(controller.length, len(bytes_))],) + ((flags,) if flags is not None else ()), {}

    # For send, simply truncate the length of the content to be sent to ``length`` and delay that by ``t`` seconds.
    wrap(s, meth='send', before=before, before_pass=True)
    wrapped_sendall = s.sendall

    # The functions that wraps sendall
    def wrapping_function(self: socket, *args: Any, **kwargs: Any) -> Any:
        bytes_ = args[0] if len(args) > 0 else kwargs.get('bytes')  # Content of the bytes parameter from send
        flags = args[1] if len(args) > 1 else kwargs.get('flags')   # flags parameter

        for i in range(0, len(bytes_), controller.length):
            time.sleep(controller.t)
            begin = i
            end = min(len(bytes_), i + controller.length)
            args = (bytes_[begin:end],) + ((flags,) if flags is not None else ())
            wrapped_sendall(*args)

    # See https://github.com/python/mypy/issues/2427#issuecomment-480263443 for the type ignoring below
    s.sendall = MethodType(wrapping_function, s)  # type: ignore

    return controller


def wrap_sending_upon_acceptance(s: socket, wrapper: Callable, param_func: Callable[[], Tuple[Any, Any]]) -> None:
    """Wrap sending functions of the connection socket returned by ``s.accept()``.

    :param s: The :class:`socket.socket` object where ``s.accept()``'s sending methods are to be wrapped.
    :param wrapper: The wrapper function.
    :param param_func: A function that returns a tuple ``(args, kwargs)``, where ``args`` are passed as positional
         arguments to the wrapper and ``kwargs`` are passed as keyword parameters.
    """

    def after(s: socket, *, original: Sequence, before: Any) -> Tuple[Any, Any]:
        conn_sock = original[0]
        conn_sock = make_socket_patchable(conn_sock, (':sending',))
        args, kwargs = param_func()
        wrapper(conn_sock, *args, **kwargs)
        return conn_sock, original[1]

    wrap_accept(s, after=after)


class DelayBeforeSendingUponAcceptanceOnceController:
    """Controller for :func:`.delay_before_sending_upon_acceptance_once`. Objects are always created and returned by
    :func:`.delay_before_sending_upon_acceptance_once` and should not be created outside the :mod:`poorconn` package.

    :param t: Same as ``t`` in :func:`delay_before_sending_upon_acceptance_once`.
    """

    __slots__ = (
        't',
    )

    def __init__(self, t: float):
        super().__init__()
        self.t: float = t
        """Same as ``t`` in :func:`delay_before_sending_upon_acceptance_once`. Updating it in the controller affects
        ``s`` in :func:`delay_before_sending_upon_acceptance_once`."""


def delay_before_sending_upon_acceptance_once(s: socket, t: float) -> DelayBeforeSendingUponAcceptanceOnceController:
    """Delay ``t`` seconds before sending for all sockets returned by ``s.accept()``, for once (first time only).
    Parameters mean the same as :func:`.delay_before_sending_once`.
    """

    controller = DelayBeforeSendingUponAcceptanceOnceController(t=t)
    wrap_sending_upon_acceptance(s, delay_before_sending_once, param_func=lambda: ((), {'t': controller.t}))
    return controller


def delay_before_sending_upon_acceptance(s: socket, t: float, length: int = 1024) -> None:
    """Delay ``t`` seconds before sending for all sockets returned by ``s.accept()``, for once (first time only).
    Parameters mean the same as :func:`.delay_before_sending`.
    """

    wrap_sending_upon_acceptance(s, delay_before_sending, param_func=lambda: ((), {'t': t, 'length': length}))
