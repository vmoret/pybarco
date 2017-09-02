"""Setup script for pybarco"""
from setuptools import setup

setup(
    name='pybarco',
    version='0.0.1',
    packages=[
        'barco', 'barco.itrack', 'barco.utils'
    ],
    package_dir={'': 'src'},
    package_data={
        'barco.itrack': ['config.json']
    },
    author='Vincent Moret',
    author_email='moret.vincent@gmail.com',
    url='https://github.com/vmoret/pybarco',
    install_requires=[
        'cryptography',
        'requests',
        'xlrd',
        'numpy',
        'pandas'
    ]
)
