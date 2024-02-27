from enum import Enum, unique
import bluetooth

@unique
class BTProtocol(Enum):
    l2cap = bluetooth.L2CAP
    rfcomm = bluetooth.RFCOMM
