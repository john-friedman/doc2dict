from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.5.0",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict','pypdfium2'
    ]
)