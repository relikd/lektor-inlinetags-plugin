from setuptools import setup

setup(
    name='lektor-inlinetags',
    py_modules=['lektor_inlinetags'],
    version='1.0',
    entry_points={
        'lektor.plugins': [
            'inlinetags = lektor_inlinetags:Main',
        ]
    }
)
