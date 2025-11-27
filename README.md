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

Testing, formatting, pre-commit hooks, CI - TODO.
