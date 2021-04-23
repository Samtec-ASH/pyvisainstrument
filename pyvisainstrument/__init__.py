"""PyVisaInstrument provides boilerplate for various NI-VISA instruments."""

try:
    from importlib.metadata import version
    __version__ = version(__name__)
except Exception:
    __version__ = "1.5.0"


from pyvisainstrument.VisaResource import VisaResource
from pyvisainstrument.KeysightPSU import KeysightPSU
from pyvisainstrument.KeysightVNA import KeysightVNA
from pyvisainstrument.KeysightDAQ import KeysightDAQ
from pyvisainstrument.NumatoRelay import NumatoRelay

__all__ = ['VisaResource', 'KeysightPSU', 'KeysightVNA', 'KeysightDAQ', 'NumatoRelay']
