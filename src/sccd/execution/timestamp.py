
class Timestamp(int):
  def __new__(cls, value=0, *args, **kwargs):
    return super(cls, cls).__new__(cls, value)

  def __repr__(self):
    return "timestamp("+format(self, 'b')+")"

  def __str__(self):
    return self.__repr__()

  def __add__(self, other):
    assert isinstance(other, Timedelta)
    return self.__class__(super().__add__(other))

  def __sub__(self, other):
    diff = super().__sub(other)
    if isinstance(other, Timedelta):
      return self.__class__(diff)
    elif isinstance(other, Timestamp):
      return Timedelta(diff)
    else:
      raise TypeError("Can't subtract '%s' object from Timestamp", str(type(other)))

class Timedelta(int):
  def __new__(cls, value=0, *args, **kwargs):
    return super(cls, cls).__new__(cls, value)

  def __repr__(self):
    return "timedelta("+format(self, 'b')+")"

  def __str__(self):
    return self.__repr__()
