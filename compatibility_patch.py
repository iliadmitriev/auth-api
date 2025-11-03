# Patch for collections.Iterable compatibility in Python 3.14+
import collections
import sys

# If we're in Python 3.14+, add back the deprecated attributes for backward compatibility
if sys.version_info >= (3, 14):
    try:
        from collections.abc import Iterable, Mapping, Sequence

        if not hasattr(collections, "Iterable"):
            collections.Iterable = Iterable
        if not hasattr(collections, "Mapping"):
            collections.Mapping = Mapping
        if not hasattr(collections, "Sequence"):
            collections.Sequence = Sequence
    except ImportError:
        # collections.abc may not be available in all environments
        pass
