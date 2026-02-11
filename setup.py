from setuptools import setup, find_packages
setup(name='mockapi', version='0.1.0', packages=find_packages(),
    install_requires=['click>=8.0','flask>=3.0'],
    entry_points={'console_scripts':['mockapi=mockapi.cli:main']}, python_requires='>=3.9')
