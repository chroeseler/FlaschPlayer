#
# The common definitions
#
from dasbus.connection import SessionMessageBus
from dasbus.identifier import DBusServiceIdentifier

# Define the message bus.
SESSION_BUS = SessionMessageBus()

# Define services and objects.
BLINKY_OPTIONS = DBusServiceIdentifier(
    namespace=("org", "blinky", "options"),
    message_bus=SESSION_BUS
)
