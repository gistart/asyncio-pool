# coding: utf8

import setuptools


with open('README.md') as fd:
    readme = fd.read()


setuptools.setup(
    name='asyncio_pool',
    version='0.2.0',
    author='gistart',
    author_email='gistart@yandex.ru',
    description='Pool of asyncio coroutines with familiar interface',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/gistart/asyncio-pool',
    license='MIT',
    packages=['asyncio_pool'],
    install_requires=['asyncio'],
    python_requires='>=3.5',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Framework :: AsyncIO",
    )
)
