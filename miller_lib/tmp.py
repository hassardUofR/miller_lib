""" Testing some simple functions to make sure the package is working """

# import numpy as np
from math import factorial

def exp_taylor(x,N=5):
    """ Returns N'th order Taylor approximation of e^x.
        Args: x (float), N (int, default=5)
    """
    result = 1
    for n in range(N):
        n += 1
        result += x**n/factorial(n)
    return result

def add_two(x,y):
    """ Adds x and y """
    return x + y

def echo(string):
    """ Prints a string """
    print(string)

