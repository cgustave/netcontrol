#!/bin/bash
export PYTHONPATH=${PYTHONPATH}:~/github/python/packages/netcontrol:./tests

NAME=vyos

echo
echo "======================================================================"
echo "= PYTHON code analysis                                               ="
echo "======================================================================"
pyflakes3 "$NAME".py
echo

echo "======================================================================"
echo "= PEP 8 codestyle check                                              ="
echo "======================================================================"
pycodestyle "$NAME".py --statistics
echo

echo "======================================================================"
echo "= UNIT TESTS                                                         ="
echo "======================================================================"
#python3 -m coverage run --rcfile tests/coveragerc  tests/test_"$NAME".py
python3 tests/test_"$NAME".py

echo
echo "======================================================================"
echo "= COVERAGE                                                           ="
echo "======================================================================"
python3 -m coverage report --show-missing 
echo

echo "======================================================================"
echo "= DOCUMENTATION                                                      ="
echo "======================================================================"
python3 -m pydoc "$NAME"  > README.md

