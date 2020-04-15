#!/bin/bash

GIT_COMMIT=$(git rev-parse HEAD)
PREVIOUS_GIT_COMMIT=$(git rev-parse HEAD^)
DELETED=$(git diff --name-only $PREVIOUS_GIT_COMMIT $GIT_COMMIT --diff-filter=D | grep "\.json$")
ADDED=$(git diff --name-only $PREVIOUS_GIT_COMMIT $GIT_COMMIT --diff-filter=A | grep "\.json$")
MODIFIED=$(git diff --name-only $PREVIOUS_GIT_COMMIT $GIT_COMMIT --diff-filter=M | grep "\.json$")

if [ -n "$DELETED" ]
then
    for DELETED_FILE in $DELETED
    do
        git show HEAD^:$DELETED_FILE > $DELETED_FILE
        adaptive-alerting disable $DELETED_FILE
    done
else
    echo "No files deleted."
fi

if [ -n "$ADDED" ]
then
    adaptive-alerting build $ADDED
else
    echo "No files added."
fi

if [ -n "$MODIFIED" ]
then
    for MODIFIED_FILE in $MODIFIED
    do
        PREVIOUS_FILE=$(echo $MODIFIED_FILE | sed s/\.json$/\.json\.previous/)
        git show HEAD^:$MODIFIED_FILE > $PREVIOUS_FILE
        DIFF_CONFIGS_FILE=$(echo $MODIFIED_FILE | sed s/\.json$/\.json\.diff/)
        adaptive-alerting diff $PREVIOUS_FILE $MODIFIED_FILE $DIFF_CONFIGS_FILE

        DELETED_CONFIGS_FILE=$(echo $MODIFIED_FILE | sed s/\.json$/\.json\.deleted/)
        cat $DIFF_CONFIGS_FILE | jq '.deleted' > $DELETED_CONFIGS_FILE
        adaptive-alerting disable $DELETED_CONFIGS_FILE

        ADDED_CONFIGS_FILE=$(echo $MODIFIED_FILE | sed s/\.json$/\.json\.added/)
        cat $DIFF_CONFIGS_FILE | jq '.added' > $ADDED_CONFIGS_FILE
        adaptive-alerting build $ADDED_CONFIGS_FILE

        MODIFIED_CONFIGS_FILE=$(echo $MODIFIED_FILE | sed s/\.json$/\.json\.modified/)
        cat $DIFF_CONFIGS_FILE | jq '.modified' > $MODIFIED_CONFIGS_FILE
        adaptive-alerting train $MODIFIED_CONFIGS_FILE

    done
else
    echo "No files modified."
fi
