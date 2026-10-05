from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.7.2",
    packages=find_packages(),
    install_requires=['selectolax==0.4.9','xmltodict','pypdfium2'
    ]
)
