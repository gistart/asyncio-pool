#! /bin/sh

py35=python3.5
pypy3=pypy3  # also 3.5 currently
py36=python3.6
py37=python3.7
#pypy3=/opt/pypy3/pypy3/bin/pypy3

default_env=$py36


for py in $py35 $pypy3 $py36 $py37
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
