
# RPN Calculator

A simple RPN calculator in Python

[![Build Status](https://travis-ci.org/mike-jg/rpn.svg?branch=master)](https://travis-ci.org/mike-jg/rpn)

### Installing and running

Run the tests:

`$ python ./test.py`

Run the REPL:

`$ python ./calc.py`

### Usage

#### Stack
All numbers are pushed onto the top of the stack

#### Operators
Valid operators are `+ - / * ^`

```
> 5 8 * 4 +
44.0
```

#### Functions
To call a function enter its name

`sqrt` pop the stack and push the square root of the popped value

```
> 64 sqrt
8.0
```

`print` print the value at the top of the stack

```
> 1 5 + print
6.0
 ```
 
`stack` print the current stack

```
> 1 2 3 4 5 6 stack
[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
```

`pop` pops the stack

```
> 1 2 3 5 pop stack
[1.0, 2.0, 3.0]
```

`clear` clear the current stack

```
> 1 2 3 4 5 clear
None
```
