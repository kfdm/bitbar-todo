
from setuptools import setup

setup(
    name='BitBar Todo',
    author='Paul Traylor',
    url='http://github.com/kfdm/bitbar-todo/',
    packages=['bbtodo'],
    install_requires=[
        'python-dateutil',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'todo = bbtodo:main'
        ]
    }
)
