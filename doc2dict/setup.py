from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.6.2",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict','pypdfium2'
    ]
)