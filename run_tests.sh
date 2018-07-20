#! /bin/sh

py35=python3.5
py36=python3.6
py37=python3.7
pypy3=/opt/pypy3/pypy3/bin/pypy3

default_env=$py36


for py in $py35 $py36 $py37 $pypy3
do
    if [ -x "$(command -v $py)" ]; then
        pyname="$(basename $py)"
        envname=".env_$pyname"

        if ! [ -d $envname ]; then
            echo "$pyname: virtual env does not exist"
        else
            $envname/bin/pytest tests
        fi
    else
        echo "$py: not found"
    fi
done
