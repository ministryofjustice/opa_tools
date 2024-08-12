#!/bin/sh

set -ex

export PYTHON_CMD=~/code/opa_tools/venv/bin/python
export DOCX2RULETXT=~/code/opa_tools/docx2ruletxt.py

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <path_to_rules_git_repo> <relative_path_to_rules_zip> <path_to_output_ruletxt_git_repo>"
  echo "Example: ruletxt2python/convert_repo.sh ~/code/laa-ccms-opa-means-v23 MeansAssessment.zip ../laa-ccms-opa-means-ruletxt"
  exit 1
fi
OPA_REPO_DIR="$1"
RULES_ZIP_PATH="$2"
OUTPUT_REPO_DIR=$(realpath "$3")

# run this from a git repo containing zipped rules ~/code/laa-ccms-opa-means-v23
cd $OPA_REPO_DIR
[ -z "$(git status --porcelain)" ] || { echo "working tree $OPA_REPO_DIR not clean" >&2; false; }
export OPA_REPO_REMOTE=$(git remote get-url origin)
git checkout main

for commit in $(git rev-list HEAD --reverse)
do

    # This will overwrite any changes.
    git checkout -f $commit

    if [[ ! -e "$RULES_ZIP_PATH" ]]; then
        echo "$RULES_ZIP_PATH does not exist, skipping $commit"
        continue
    fi

    export COMMIT_MESSAGE=$(git show -s --format=%B)
    export COMMIT_DATE=$(git show -s --format=%cd)
    export COMMIT_AUTHOR=$(git show -s --format=%an)
    export COMMIT_EMAIL=$(git show -s --format=%ae)

    rm -rf $OUTPUT_REPO_DIR/*

    rm -rf /tmp/laa-ccms-opa-means-v23-extracted
    unzip $RULES_ZIP_PATH -d /tmp/laa-ccms-opa-means-v23-extracted || {
        echo "Failed to unzip $RULES_ZIP_PATH, skipping to the next commit."
        continue
    }
    cd /tmp/laa-ccms-opa-means-v23-extracted
    $PYTHON_CMD $DOCX2RULETXT -d /tmp/laa-ccms-opa-means-v23-extracted -o $OUTPUT_REPO_DIR
    cd $OUTPUT_REPO_DIR
    
    git add .
    export GIT_AUTHOR_DATE="$COMMIT_DATE"
    export GIT_COMMITTER_DATE="$COMMIT_DATE" 
    export COMMIT_MESSAGE="$(cat <<EOF
$COMMIT_MESSAGE

--
This commit is a conversion by docx2ruletxt.py from the original:
$OPA_REPO_REMOTE $commit
EOF
)"
    git commit -m "$COMMIT_MESSAGE" --author="$COMMIT_AUTHOR <$COMMIT_EMAIL>" --allow-empty

    cd $OPA_REPO_DIR
    # exit 1  # for testing
done