from setuptools import setup

setup(
    name="miller_lib",
    version="0.0",
    description="A package of Miller group photonics design functions, classes, and structures",
    author="Brian Hassard",
    author_email="bhassard@ur.rochester.edu",
    packages=["tmp"],
    install_requires=[
    "numpy",
    "scipy",
    "gdsfactory",
    "matplotlib",
    "klayout"],
)