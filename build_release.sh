#!/bin/bash
set -e

SERVICE_NAME="marian-client"
NOW="$(date +'%B %d, %Y')"
BASE_STRING=$(cat VERSION)
BASE_LIST=($(echo "$BASE_STRING" | tr '.' ' '))
V_MAJOR=${BASE_LIST[0]}
V_MINOR=${BASE_LIST[1]}
V_PATCH=${BASE_LIST[2]}
echo -e "Current version: $BASE_STRING"
V_MINOR=$((V_MINOR + 1))
V_PATCH=0
SUGGESTED_VERSION="$V_MAJOR.$V_MINOR.$V_PATCH"

INVENV=$(python -c 'import sys; print ("1" if hasattr(sys, "base_prefix") else "0")')
CREDS_LOCATION=$1


check_credential_file_exists ()
{
    if [ ! -z "${CREDS_LOCATION_ENV}" ]; then
        echo "credentials were passed in environment"
        CREDS_LOCATION=${CREDS_LOCATION_ENV}
        PYPIRC="creds"
    elif [ ! -z "${CREDS_LOCATION}" ]; then
        echo "credentials were passed in as argument"
        PYPIRC="creds"
    elif [ -f .pypirc ]; then
        echo "found .pypirc in project directory..."
        PYPIRC="here"
    elif [ -f ~/.pypirc ]; then
        echo "found .pypirc in user home directory..."
        PYPIRC="root"
    else
        echo "## MISSING .pypirc file, can't release to PyPi!"
        exit 1
    fi
}

activate_venv_if_not_activated ()
{
    if [ "$INVENV" -eq 1 ]; then
        echo "Already in virtualenv..."
    else
        echo "Not in virtualenv, attempting to activate."
        if [ -d venv ]; then
            echo ""
            echo "venv directory already exists"
            echo ""
        else
            echo ""
            echo "virtualenv doesn't yet exist, creating..."
            echo ""
            python3 -m venv venv
        fi
        echo "activating venv"
        # shellcheck disable=SC1091
        . venv/bin/activate
    fi
}

update_deps ()
{
    pip install -U setuptools wheel
    pip install -r requirements-dev.txt
    pip install -r requirements.txt
}

run_tests ()
{
    echo "running test suite"
    python -m pytest -v
}

bump_version ()
{
    echo "$SUGGESTED_VERSION" > VERSION
}

update_changelog ()
{
    # requires git access
    echo "## $SUGGESTED_VERSION ($NOW)" > tmpfile
    {
        echo ""
        git log --pretty=format:"- %s" "v$BASE_STRING"..HEAD
        echo ""
        echo ""
        cat CHANGELOG.md
    } >> tmpfile
    mv tmpfile CHANGELOG.md

    git add CHANGELOG.md VERSION marian_client/version.py
    git commit -m "Bump version to ${SUGGESTED_VERSION}."
    git tag -a -m "Tag version ${SUGGESTED_VERSION}." "v$SUGGESTED_VERSION"
    git push origin --follow-tags
}

create_dist ()
{
    echo "generating source distribution - this step bumps version.py to match VERSION"
    python3 setup.py sdist
}

upload_to_pypi ()
{
    echo "uploading to pypi"
    if [ $PYPIRC = "here" ]; then
        twine upload --config-file .pypirc dist/"$SERVICE_NAME"-"$SUGGESTED_VERSION".tar.gz
    elif [ $PYPIRC = "creds" ]; then
        twine upload --config-file "$CREDS_LOCATION" dist/"$SERVICE_NAME"-"$SUGGESTED_VERSION".tar.gz
    else
        twine upload --config-file ~/.pypirc dist/"$SERVICE_NAME"-"$SUGGESTED_VERSION".tar.gz
    fi
}

# this doesn't work, it starts thinking it is in a venv, but then can't deactivate
cleanup ()
{
    echo "uninstalling dev dependencies..."
    python -m pip uninstall -y -q -r requirements-dev.txt
    echo "leaving virtualenv"
    deactivate || echo "wasn't in venv"
}

#########################
# Actually run the code #
#########################

check_credential_file_exists
activate_venv_if_not_activated
update_deps
run_tests  # damn, need to write tests
bump_version
create_dist
update_changelog
upload_to_pypi
cleanup
