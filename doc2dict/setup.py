from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.4.9",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict','pypdfium2'
    ]
)