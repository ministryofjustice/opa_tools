# OPA Tools

## Parse docx

Parses an OPA rule document.

### Setup

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Run

To parse one file:
```
source venv/bin/activate
python parse_docx.py ../laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR\ System\ Rules.docx
```

### Parse all .docx files

Locate the folders for the extracted zip and markdown repo (adjust these if you put them elsewhere):

```sh
export IN_DIR=~/code/laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/rules
export OUT_DIR=~/code/laa-ccms-opa-means-assessment-python
export PYTHON_CMD=~/code/opa_analysis/venv/bin/python
export PARSE_PY=~/code/opa_analysis/parse_docx.py
```

Convert the Word docs to python:

```sh
cd $IN_DIR
# the next command is creating directories - you can ignore "File exists" errors
find . -type d -print0 | sed 's/ /_/g' | xargs -0 -I % -n1 mkdir "$OUT_DIR/%"
find . -name "*.docx" -exec sh -c '$PYTHON_CMD $PARSE_PY "$0" "$OUT_DIR/${0// /_}.py" || echo "$0"' {}  \;
```

Commit the changes to this repo:
```sh
cd $OUT_DIR
```

## Importer

Imports a CSV into a sqlite database. It's useful to import a CSV of OPA attributes, so that you can then use SQL to query it.

```
source venv/bin/activate
python import.py
```
