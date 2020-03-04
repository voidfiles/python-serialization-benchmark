# Python Serialization Benchmark

This [repository](http://github.com/voidfiles/python-serialization-benchmark) maintains a set of benchmarks for python serialization frameworks.

You can find the latest benchmarks on [this page](https://voidfiles.github.io/python-serialization-benchmark/).

Currently the following projects are benchmarked.

* [Django REST framework](http://www.django-rest-framework.org/)
* [serpy](http://serpy.readthedocs.io/)
* [Marshmallow](https://marshmallow.readthedocs.io/en/latest/)
* [Strainer](https://github.com/voidfiles/strainer)
* [Lollipop](http://lollipop.readthedocs.io/en/latest/)
* [kim](http://kim.readthedocs.io/en/latest/)
* [toasted-marshmallow](https://github.com/lyft/toasted-marshmallow)
* [Colander](https://docs.pylonsproject.org/projects/colander/en/latest/)
* [Lima](https://github.com/b6d/lima/)
- [Serpyco](https://gitlab.com/sgrignard/serpyco)

Along with a baseline custom function that doesn't use a framework.


## Running the test suite

A Docker container is bundled with the repository which you can use to run the benchmarks. Firstly make sure you have Docker installed.

1. Install Docker

2. Build the container `$ docker-compose build`

3. Run the tests. `$ docker-compose run --rm tests`
