#! /bin/sh

pypy3=pypy3
py35=python3.5
py36=python3.6
py37=python3.7
py38=python3.8
py39=python3.9

default_env=$py37


todo=${@:-"./tests"}

for py in $py35 $py36 $py37 $py38 $py39 $pypy3
do
    echo ""
    if [ -x "$(command -v $py)" ]; then
        pyname="$(basename $py)"
        envname=".env_$pyname"

        if ! [ -d $envname ]; then
            echo "$pyname: virtual env does not exist"
        else
            echo "$pyname: running for $todo"
            $envname/bin/pytest --continue-on-collection-errors $todo
        fi
    else
        echo "$py: not found"
    fi
done
