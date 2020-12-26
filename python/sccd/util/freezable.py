
# Slight performance hit when setting an attribute.
# Read operations unchanged.
class Freezable:
    __slots__ = ["_Freezable__frozen"]

    def __init__(self):
        super().__setattr__("_Freezable__frozen", False)

    def freeze(self):
        super().__setattr__("_Freezable__frozen", True)

    def __setattr__(self, key, value):
        assert not self._Freezable__frozen
        super().__setattr__(key, value)
