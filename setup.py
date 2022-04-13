from setuptools import setup

with open('README.md') as fp:
    longdesc = fp.read()

setup(
    name='lektor-inlinetags',
    py_modules=['lektor_inlinetags'],
    install_requires=['lektor-groupby>=0.9.6'],
    entry_points={
        'lektor.plugins': [
            'inlinetags = lektor_inlinetags:InlineTagsPlugin',
        ]
    },
    author='relikd',
    url='https://github.com/relikd/lektor-inlinetags-plugin',
    version='0.9.1',
    description='Auto-detect and reference tags inside written text.',
    long_description=longdesc,
    long_description_content_type="text/markdown",
    license='MIT',
    python_requires='>=3.6',
    keywords=[
        'lektor',
        'plugin',
        'blog',
        'tags',
        'tagging',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Environment :: Plugins',
        'Framework :: Lektor',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
