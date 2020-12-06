import abc

class Visitor:
    @abc.abstractmethod
    def default(self):
        pass

class Visitable:
    def accept(self, visitor: Visitor):
        typename = type(self).__qualname__.replace(".", "_")
        lookup = "visit_" + typename
        try:
            return getattr(visitor, lookup)(self)
        except AttributeError:
            return visitor.default(what)