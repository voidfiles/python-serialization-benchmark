
class ChildTestObject(object):
    def __init__(self, multiplier=None):
        self.w = 1000 * multiplier if multiplier else 100
        self.x = 20 * multiplier if multiplier else 20
        self.y = 'hello' * multiplier if multiplier else 'hello'
        self.z = 10 * multiplier if multiplier else 10


class ParentTestObject(object):
    def __init__(self):
        self.foo = 'bar'
        self.sub = ChildTestObject()
        self.subs = [ChildTestObject(i) for i in xrange(10)]

    def bar(self):
        return 5
