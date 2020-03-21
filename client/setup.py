from setuptools import find_packages
from setuptools import setup


setup(
    name="x2webrtc",
    version="0.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=7.0.0,<7.1.0",
        "aiortc>=0.9.0,<0.10.0",
        "av>=7.0.0,<8.0.0",
        "dacite>=1.2.0,<1.3.0",
        "numpy>=1.18.0,<1.19.0",
        "python-xlib>=0.26,<1.0",
    ],
    extras_require={"test": ["pytest>=5.0.0,<6.0.0"]},
)
