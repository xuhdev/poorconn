# Copyright (C) 2020--2021  Hong Xu <hong@topbug.net>

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

"The main package of Poorconn. It contains functions that simulate Poor Network Conditions."

from ._accept import close_upon_acceptance
from ._send import (DelayBeforeSendingController,
                    DelayBeforeSendingOnceController,
                    DelayBeforeSendingUponAcceptanceController,
                    DelayBeforeSendingUponAcceptanceOnceController,
                    delay_before_sending,
                    delay_before_sending_once,
                    delay_before_sending_upon_acceptance,
                    delay_before_sending_upon_acceptance_once)
from ._socket import make_socket_patchable, PatchableSocket

from ._version import version as __version__
