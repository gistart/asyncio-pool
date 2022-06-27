#! /bin/sh

pypy3=pypy3
py35=python3.5
py36=python3.6
py37=python3.7
py38=python3.8
py39=python3.9
py310=python3.10

default_env=$py37


todo=${@:-"./tests"}

# test without mypy
for py in $pypy3 $py35
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

# test >=3.6 with mypy
for py in $py36 $py37 $py38 $py39 $py310
do
    echo ""
    if [ -x "$(command -v $py)" ]; then
        pyname="$(basename $py)"
        envname=".env_$pyname"

        if ! [ -d $envname ]; then
            echo "$pyname: virtual env does not exist"
        else
            echo "$pyname: running for $todo (with mypy)"
            $envname/bin/pytest --mypy --continue-on-collection-errors $todo
        fi
    else
        echo "$py: not found"
    fi
done
