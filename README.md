# Quantum Math

This library contains implementation of various mathematical functions for a 
fault-tolerant quantum computing. The functions are implemented in Python,
using PsiQuantum's [Workbench](https://docs.construct.psiquantum.com/workbench/index.html) library.
Each function is represented as a 
[Qubrick](https://docs.construct.psiquantum.com/workbench/new-tutorials/Qubricks.html).

This library was built as a research project done as a part of 
[Quantum Open Source Foundation](https://qosf.org/)'s mentorship program, cohort 11.

The author is [Dmytro Fedoriaka](https://github.com/fedimser).
The author thanks mentors Mariia Mykhailova and Sean Greenway for help and guidance
during this project. The author also thanks 
[PsiQuantum](https://www.psiquantum.com/)  for early access to their
quantum computing library, Workbench.

## Goals of the project

* Implement a library of mathematical functions.
* Support integer and real (fixed-precision) numbers.
* Implement multiple algorithms for the same function, where possible.
* Test the implementations using a simulator.
* Implement symbolic resource estimation for functions in the library.
* Run experiments comparing numeric and symbolic resource estimation for 
functions in the library.

## Implemented functions

Below is the list of functions we implemented.

All functions except in `uint_arith` operate on real fixed-precision quantum 
numbers.

* [qmath/uint_arith](/qmath/uint_arith) - arithmetic functions on unsigned integers (QUInt). These include:
  * Adders: [TTK](https://arxiv.org/abs/0910.2530) and [Cuccaro](https://arxiv.org/abs/quant-ph/0410184).
  * Multipliers: [JHHA](https://arxiv.org/abs/1608.01228) and [MCT](https://arxiv.org/abs/1706.05113)
  * Dividers: restoring and non-restoring, from 
[this paper](https://arxiv.org/pdf/1809.09732).
  * Algorithms in this directory were ported from Q# implementation in 
[this repository](https://github.com/fedimser/quant-arith-re).
  * This is only part dealing with integers, all other functions are for QFixed
  (real fixed-precision) quantum numbers.
* [qmath/poly/horner.py](qmath/poly/horner.py) - evaluating polynomials using Horner Scheme.
* [qmath/poly/piecewise.py](qmath/poly/piecewise.py) - evaluating arbitrary 
smooth functions on an interval using piecewise polynomial approximation and parallel Horner Scheme.
  * Algorithm from [this paper](https://arxiv.org/abs/1805.12445).
  * [Demo](notebooks/accuracy/sin.ipynb).
* [qmath/func/common.py](qmath/func/common.py) - basic functions:
  * Absolute value.
  * Addition (quantum-classical and quantum-quantum) - wrapper around 
    GidneyAdd from Workbench, but with corrected resource estimation.
  * Subtraction (by reduction to addition).  
  * Negation (by reduction to addition).  
  * Quantum-quantum multiplication - wrapper around GidneyMultiplyAdd from 
    Workbench, but with corrected resource estimation.
  * Quantum-classical multiplication.
* [qmath/func/compare.py](qmath/func/compare.py) - comparison.
* [qmath/func/bits.py](qmath/func/bits.py) - bitwise functions (such as finding 
  most significant bit).
* [qmath/func/fbe.py](qmath/func/fbe.py) - evaluating certain mathematical 
  functions using function-value binary expansion method.
  * Algorithms from [this paper](https://arxiv.org/abs/2001.00807).
  * Supported functions: sin, cos, logarithm (base 2 and in arbitrary base).
  * Functions described in the paper that we didn't implement, but their implementation uses similar algorithm: 2^x, e^x, Arcsin, Arccos, Arctan, Arccot.
  * [Demo](notebooks/accuracy/cos_fbe.ipynb) (for cos). 
  * [Demo](notebooks/accuracy/log_fbe.ipynb) (for logarithm). 
* [qmath/func/inv_sqrt.py](qmath/func/inv_sqrt.py) - evaluating inverse square
   root using the Newton-Raphson method. 
  * Algorithm from [this paper](https://arxiv.org/abs/1805.12445) (Appendix C).
  * [Demo](notebooks/accuracy/inv_sqrt.ipynb).
* [qmath/func/square.py](qmath/func/square.py) - 2 implementations of square.
  * One is by reduction to multiplication.
  * The other is using algorithm from Lemma 6 in [this paper](https://arxiv.org/abs/2105.12767), extended to support real numbers.
* [qmath/func/sqrt.py](qmath/func/sqrt.py) - square root.
  * It uses `qubricks.Sqrt` from Workbench. However, it extends integer square 
    root algorithm to work for QFixed with any radix size using at most one 
    padding qubit. It also supports efficiently computing `sqrt(x/2)`.
  * Uses algorithm from [this paper](https://arxiv.org/abs/1712.08254).
* [qmath/utils/lookup.py](qmath/utils/lookup.py) - table lookup from 
  [this paper](https://arxiv.org/pdf/1805.03662).
* [qmath/utils/perm.py](qmath/utils/perm.py) - permutations and rotations.

## Resource estimation

For most implemented functions we also implemented symbolic resource estimation 
and added tests that symbolic resource estimation matches numeric one.

Symbolic RE is defined as a formula of input sizes (number of qubits and, in
some cases, radix size, i.e. number of bits representing fractional part).

## Quantum compiler

We implemented a prototype for "quantum compiler" - automatic circuit generator 
for a mathematical function. It takes an expression describing function of one 
or more arguments and generates a quantum circuit implementing that function.
It manages allocation of all auxiliary qubits and tries to optimize resource 
usage.

Our prototype only supports addition, subtraction and multiplication.

[Here](notebooks/compiler_demo.ipynb) is a demo notebook. It also includes 
ideas on how this can be improved.

## Intended usage of the library

We hope that this library will be useful for researchers as a collection of quantum algorithms implemented in PsiQuantum's
Workbench library.

If you intend to use the library, you may clone repository locally or just copy
the code. MIT license allows to do this without attribution but you may link
to this github repository to give credit.

This library also serves as an example of using PsiQuantum's Workbench for
developing algorithms for fault-tolerant quantum computers.


## Development

### Setup

Clone repository into `/home/coder/projects` in PsiQDE instance. Then:

```
cd /home/coder/projects/qmath
python -m pip install -e .[dev]  # Install dependencies.
pre-commit install               # Install pre-commit hooks.
pytest -m smoke                  # Run tests.
```

### Testing

We use pytest for testing. Some tests take long time to run so we use pytest
markers to easily skip unnecessary tests:
* `smoke` - "smoke tests" (quick checks for basic functionality). These are run by precommit hook, so these include very few fast tests.
* `slow` - slow tests, take >1s to run.
* `re` - resource estimation tests.

Run test as follows:
* During development, run tests in a single file, e.g. `pytest ./qmath/add/adders_test.py`.
* For quick "smoke test" run `pytest -m smoke`.
* Run `pytest -m "not slow"` to check most of functionality, this runs in about 10 seconds. If this passes, most likely you didn't break anything.
* Run `pytest -m re` to run all resource estimation tests.
* Run `pytest` only when you really want to run all the tests. This also would be run by CI, if we could do it.


### Formatting

This repository uses [Black formatter](https://github.com/psf/black). 
Recommended setup for VSCode is:
* Install extension "[Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)".
* Use Ctrl+Shift+I to format file.

### Pre-commit hooks

This repository uses pre-commit hooks to run formatter and some tests. 
* If "black" hook fails, you need to re-format-code, just run `black .`.
* If "pytest" hook fails, you need to fix failing tests.
* After fixing the issue, commit again.


This is necessary because we currently cannot run tests on Github Actions.


### Profiling

To profile a piece of code:
* Put the code you want to profile in profiling/code.py.
* Run `./profiling/run.sh`
* Download file profiling/profile.json locally (right-click -> Download...).
* Go to https://www.speedscope.app/ and upload profile.json.