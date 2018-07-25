#! /bin/sh

# build
rm -r *.egg_info build
.env/bin/python setup.py sdist bdist_wheel

# upload
#.env/bin/twine upload -u gistart --skip-existing dist/*
