#!/bin/bash

function buildEnvironment(){

    SOURCE="${BASH_SOURCE[0]}"

    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ ${SOURCE} != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

    cd ${DIR}/../
    ENV=app-env
    REQUIREMENTS=requirements.txt

    unamestr=`uname`
    if [[ "$unamestr" == 'Darwin' ]]; then
        export CC=/usr/bin/llvm-gcc
    fi

#    virtualenv $ENV
    python3 -m venv ${ENV}

    PYTHONENV=${ENV}/bin
    SRCROOT=src

    #activate env and add project src to PYTHONPATH
    chmod +x ${PYTHONENV}/activate
    ${PYTHONENV}/activate

    export PYTHONPATH=${PYTHONPATH}:${SRCROOT}

    if [ -f ${REQUIREMENTS} ]; then
        ${PYTHONENV}/pip install -r ${REQUIREMENTS}
    fi
}

buildEnvironment
