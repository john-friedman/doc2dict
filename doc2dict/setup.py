from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict'
    ],
    python_requires=">=3.8"
)