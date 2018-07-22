#! /bin/sh

## 3.5 and pypy (which is also 3.5) are disalbed because of async generators
py35=python3.5
pypy3=pypy3
py36=python3.6
py37=python3.7

default_env=$py36


todo=${@:-"./tests"}

for py in $py35 $py36 $py37 $pypy3
do
    echo ""
    if [ -x "$(command -v $py)" ]; then
        pyname="$(basename $py)"
        envname=".env_$pyname"

        if ! [ -d $envname ]; then
            echo "$pyname: virtual env does not exist"
        else
            echo "$pyname: running for $todo"
            $envname/bin/pytest $todo
        fi
    else
        echo "$py: not found"
    fi
done
