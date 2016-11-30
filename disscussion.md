## The Benchmark

Each framework is asked to serialize a list of 2 objects a 1000 times, and then 1 object a 1000 times.

This is the current object that is being serialized.

```python
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

benchmark_object = ParentTestObject()
```

## Discussion

Serialization from python objects to JSON, XML, or other transmission formats is a common task for many web related projects. In order to fill that need a number of frameworks have arised. While their aims are similar, they don't all share the same attributes. Here are how some of the features comapre.

<table class="table">
  <thead>
    <tr>
        <td>Project</td>
        <td>Serialization</td>
        <td>Encoding</td>
        <td>Deserialization</td>
        <td>Validation</td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="http://www.django-rest-framework.org/">Django REST Framework</a></td>
      <td><a href="http://www.django-rest-framework.org/api-guide/serializers/">Yes</a></td>
      <td><a href="http://www.django-rest-framework.org/api-guide/renderers/">Yes</a></td>
      <td><a href="http://www.django-rest-framework.org/api-guide/validators/">Yes</a></td>
      <td><a href="http://www.django-rest-framework.org/api-guide/validators/">Yes</a></td>
    </tr>
    <tr>
      <td><a href="http://serpy.readthedocs.io/">serpy</a></td>
      <td><a href="http://serpy.readthedocs.io/en/latest/#examples">Yes</a></td>
      <td>No</td>
      <td>No</td>
      <td>No</td>
    </tr>
    <tr>
      <td><a href="https://marshmallow.readthedocs.io/en/latest/">marshmallow</a></td>
      <td><a href="https://marshmallow.readthedocs.io/en/latest/quickstart.html#serializing-objects-dumping">Yes</a></td>
      <td><a href="https://marshmallow.readthedocs.io/en/latest/quickstart.html#serializing-objects-dumping">Yes</a></td>
      <td><a href="https://marshmallow.readthedocs.io/en/latest/quickstart.html#deserializing-objects-loading">Yes</a></td>
      <td><a href="https://marshmallow.readthedocs.io/en/latest/quickstart.html#validation">Yes</a></td>
    </tr>
    <tr>
      <td><a href="https://github.com/maximkulkin/lollipop">Lollipop</a></td>
      <td><a href="http://lollipop.readthedocs.io/en/latest/quickstart.html#serializing-data">Yes</a></td>
      <td>No</td>
      <td><a href="http://lollipop.readthedocs.io/en/latest/quickstart.html#deserializing-data">Yes</a></td>
      <td><a href="http://lollipop.readthedocs.io/en/latest/quickstart.html#validation">Yes</a></td>
    </tr>
    <tr>
      <td><a href="https://github.com/voidfiles/strainer">strainer</a></td>
      <td><a href="https://github.com/voidfiles/strainer#serialization-example">Yes</a></td>
      <td><a href="https://github.com/voidfiles/strainer/blob/master/strainer/encoders.py#L25">Yes</a></td>
      <td><a href="https://github.com/voidfiles/strainer#validation">Yes</a></td>
      <td><a href="https://github.com/voidfiles/strainer#validation">Yes</a></td>
    </tr>
  </tbody>
</table>

* **Serialization**: Does the framework provide a way of serializing python objects to simple datastructures
* **Encoding**: Does the framework provide a way of encoding data into a wire format
* **Deserialization**: Does the framework provide a way of deserializing simple data structures into complex data structures
* **Validation**: Does the framework provide a way of validating datastructures, and reprorting error conditions
* **Part of Framework**: Is serialization apart of a larger framework
