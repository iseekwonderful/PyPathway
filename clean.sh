#! /bin/sh

# this file clean pyc, __pycache__ and other meanness file in the project
# clean the pyc/pyo/__pycache__ file

find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

rm -r build
rm -r dist
rm -r assets
rm -r caches
