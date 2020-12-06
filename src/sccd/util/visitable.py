import abc

class Visitor:
    @abc.abstractmethod
    def default(self):
        pass

class Visitable:
    def accept(self, visitor: Visitor):
        typename = type(self).__qualname__.replace(".", "_")
        lookup = "visit_" + typename
        if hasattr(visitor, lookup):
            return getattr(visitor, lookup)(self)
        else:
            return visitor.default(typename)
