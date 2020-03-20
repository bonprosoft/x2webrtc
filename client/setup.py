from setuptools import find_packages
from setuptools import setup


setup(
    name="momo",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=7.0.0,<7.1.0",
        "aiortc>=0.9.0,<0.10.0",
        "av>=7.0.0,<8.0.0",
        "numpy>=1.18.0,<1.19.0",
        "python-xlib>=0.26,<1.0",
    ],
)
