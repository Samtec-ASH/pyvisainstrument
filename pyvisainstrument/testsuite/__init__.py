
"""Provides minimal dummy TCP-based instruments to test against in development
and CI/CD. Still missing significant logic and functionality.
"""

__version__ = '0.9.0'

from pyvisainstrument.testsuite.DummyTCPInstrument import DummyTCPInstrument
from pyvisainstrument.testsuite.DummyDAQ import DummyDAQ
from pyvisainstrument.testsuite.DummyVNA import DummyVNA
from pyvisainstrument.testsuite.DummyPS import DummyPS

__all__ = ['DummyTCPInstrument', 'DummyVNA', 'DummyDAQ', 'DummyPS']
