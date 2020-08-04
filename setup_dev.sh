#! /bin/sh

pypy3=pypy3
py35=python3.5
py36=python3.6
py37=python3.7
py38=python3.8
py39=python3.9

default_env=$py37


for py in $pypy3 $py35 $py36 $py37 $py38 $py39
do
    if [ -x "$(command -v $py)" ]; then
        pyname="$(basename $py)"
        envname=".env_$pyname"

        if ! [ -d $envname ]; then
            echo "$pyname: creating new env at $envname"
            $py -m venv --system-site-packages $envname

            echo "$pyname: upgrading pip"
            $envname/bin/pip install --upgrade pip
        fi

        if ! [ -d ".env" ] && [ "$py" = "$default_env" ]; then
            ln -s $envname .env
        fi

        $envname/bin/pip install --upgrade -r reqs-dev.txt

    else
        echo "$py: not found"
    fi
done
