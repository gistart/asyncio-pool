# coding: utf8

import setuptools


github_url = 'https://github.com/gistart/asyncio-pool'

readme_lines = []
with open('README.md') as fd:
    readme_lines = filter(None, fd.read().splitlines())
readme_lines = list(readme_lines)[:3]
readme_lines.append('Read more at [github page](%s).' % github_url)
readme = '\n\n'.join(readme_lines)


setuptools.setup(
    name='asyncio_pool',
    version='0.5.0',
    author='gistart',
    author_email='gistart@yandex.ru',
    description='Pool of asyncio coroutines with familiar interface',
    long_description=readme,
    long_description_content_type='text/markdown',
    url=github_url,
    license='MIT',
    packages=['asyncio_pool'],
    # install_requires=['asyncio'],  # where " openstack/deb-python-trollius asyncio" comes from???
    python_requires='>=3.5',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    )
)
