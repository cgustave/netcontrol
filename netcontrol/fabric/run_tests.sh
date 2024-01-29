#!/bin/bash

NAME=fabric

if [ -n "$1" ]; then 

    echo "Test with direct connection to fortipoc at $1"
    # Position pythonpath to avoid loading our faked libs ssh adn rquest
    export PYTHONPATH=$PYTHONPATH:/home/cgustave/github/python/packages/netcontrol
    python3 tests/test_"$NAME".py
else
    echo "Run unittests"
    export PYTHONPATH=$PYTHONPATH:/home/cgustave/github/python/packages/netcontrol/netcontrol/fabric:/home/cgustave/github/python/packages/netcontrol
    python3 -m coverage run --rcfile tests/coveragerc  tests/test_"$NAME".py
fi


