from setuptools import setup, find_packages

setup(
    name="doc2dict",
    version="0.2.2",
    packages=find_packages(),
    install_requires=['selectolax','xmltodict'
    ],
    python_requires=">=3.8"
)