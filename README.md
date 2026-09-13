# Python Serialization Benchmark

This [repository](http://github.com/voidfiles/python-serialization-benchmark) maintains a set of benchmarks for python serialization frameworks.

You can find the latest benchmarks on [this page](https://voidfiles.github.io/python-serialization-benchmark/).

Currently the following projects are benchmarked.

* [Django REST Framework](http://www.django-rest-framework.org/)
* [serpy](http://serpy.readthedocs.io/)
* [Marshmallow](https://marshmallow.readthedocs.io/en/latest/)
* [Strainer](https://github.com/voidfiles/strainer)
* [Lollipop](http://lollipop.readthedocs.io/en/latest/)
* [Kim](http://kim.readthedocs.io/en/latest/)
* [Toasted Marshmallow](https://github.com/lyft/toasted-marshmallow)
* [Colander](https://docs.pylonsproject.org/projects/colander/en/latest/)
* [Lima](https://github.com/b6d/lima/)
- [Serpyco](https://gitlab.com/sgrignard/serpyco)
* [Avro](https://avro.apache.org/)

Along with a baseline custom function that doesn't use a framework.

## Latest benchmark

Run on September 13, 2026, using the bundled Python 3.14 Docker image.

```
Library                  Many Objects (seconds)    One Object (seconds)    Relative
---------------------  ------------------------  ----------------------  ----------
serpyco                              0.00333214              0.00165772     1
Custom                               0.00395489              0.00182962     1.15925
lima                                 0.0039432               0.00200844     1.19275
Pickle                               0.00661707              0.00627398     2.58345
serpy                                0.00961614              0.0049448      2.9181
Strainer                             0.0123241               0.00605392     3.68307
Toasted Marshmallow                  0.0188358               0.0102854      5.83606
Colander                             0.0491045               0.0235727     14.565
Avro                                 0.0878501               0.0419264     26.008
Lollipop                             0.102559                0.0432115     29.2132
Marshmallow                          0.112552                0.0537682     33.3316
kim                                  0.173473                0.0878582     52.3724
Django REST Framework                0.159167                0.121788      56.3051
```


## Running the test suite

A Docker container is bundled with the repository which you can use to run the benchmarks. Firstly make sure you have Docker installed.

1. Install Docker

2. Build the container `$ docker-compose build`

3. Run the tests. `$ docker-compose run --rm tests`
