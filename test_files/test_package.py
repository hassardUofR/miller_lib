""" Test to see if the Python package is being accessed correctly 

    This file runs a very simple function included in the miller_lib package 
    (a function that adds two numbers) to ensure that the package is working correctly.
    The output should print the sum into the terminal.
"""

from miller_lib import add_two

a = 5
b = 8

print(add_two(a,b))
