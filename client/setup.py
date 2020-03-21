from setuptools import find_packages, setup

setup(
    name="x2webrtc",
    description="Forward X window through WebRTC as a MediaStream",
    version="0.0.1",
    author="Yuki Igarashi",
    author_email="me@bonprosoft.com",
    url="https://github.com/bonprosoft/x2webrtc",
    license="MIT License",
    packages=find_packages(),
    install_requires=[
        "Pillow>=7.0.0,<7.1.0",
        "aiortc>=0.9.0,<0.10.0",
        "av>=7.0.0,<8.0.0",
        "dacite>=1.2.0,<1.3.0",
        "dataclasses; python_version < '3.7'",
        "numpy>=1.18.0,<1.19.0",
        "python-xlib>=0.26,<1.0",
    ],
    extras_require={"test": ["pytest>=5.0.0,<6.0.0"]},
    entry_points={"console_scripts": ["x2webrtc=x2webrtc.cli:main"]},
)
