import collections
from collections import abc


# The latest available Toasted Marshmallow and Lollipop releases still use the
# legacy locations for these ABCs. Install their modern equivalents before
# importing either serializer.
for _name in ('Iterable', 'Mapping', 'MutableSet', 'Sequence'):
    if not hasattr(collections, _name):
        setattr(collections, _name, getattr(abc, _name))

del _name
