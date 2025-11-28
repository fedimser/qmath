# Quamtum Math

This library contains implementation of various mathematical functions for a 
fault-taulerant quantum computing. The functions are implemented in Python,
using PsiQuantum's [Workbench](https://docs.construct.psiquantum.com/workbench/index.html) library.
Each function is represented as a 
[Qubrick](https://docs.construct.psiquantum.com/workbench/new-tutorials/Qubricks.html).

This library is an ongoing research project done as a part of 
[Quantum Open Source Foundation](https://qosf.org/)'s mentorhsip program, cohort 11.

The authors are [Dmytro Fedoriaka](https://github.com/fedimser), 
[Thiri Yamin Hsu](https://github.com/ThiriYaminHsu) and Sanskriti Joshi.
The mentors are Mariia Mykhailova and Sean Greenway.

# Goals of the project

* Implement a library of mathematical functions, including artihtmetic
(addition, multiplication, division and modular exponentiation) functions,
trigonometric and other functions.
* Support integer and real numbers.
* Implement multiple algorithms for the same function, where possible.
* Test our implementations using a simulator.
* Implement symbolic resource estimation for functions in the library.
* Run experiments comparing numeric and symbolic resource estimation for 
functions in the library.

# Repository structure

* `qmath` - function implementations. They are groupped in folders by function
type (e.g. addition, multiplication, division). Each folder has mutiple Python 
files, one file generally corresponding to an academic paper where ceetain 
algorithm was described, with reference to the paper at the top.
* `notebooks` - demo notebooks.


# Available functions

* Addition - TODO.
* Multiplication - TODO.
* Division - TODO.
* Modular exponentiation - TODO.

# Development

### Setup

Clone repository into `/home/coder/projects` in PsiQDE instance. Then:

```
cd /home/coder/projects/qmath
python -m pip install -e .[dev]  # Install dependencies.
pre-commit install               # Install pre-commit hooks.
pytest                           # Run tests.
```

### Testing

We use pytest for testing. To run all tests, run `pytest`. You can also
run tests in a single file, e.g. `pytest ./qmath/add/adders_test.py`.

### Formatting

This repository uses [Black formatter](https://github.com/psf/black). 
Recommended setup for VSCode is:
* Install extension "[Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)".
* Use Ctrl+Shift+I to format file.

### Pre-commit hooks

This repository uses pre-commit hooks to run formatter and all tests. 
* If "black" hook fails, you need to re-format-code, just run `black .`.
* If "pytest" hook fails, you need to fix failing tests.
* After fixing the issue, commit again.


This is necessary because we currently cannot run tests on Gihub Actions.

In the future, if tests will take too long, we will allow marking some of them 
as "slow", and run only "fast" tests on pre-commit hook.
