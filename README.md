# OPA Tools

A selection of tools for working with OPA (Oracle Policy Automation) rulebases.

## Setup

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Get the OPA rulebase, in the original Word & Excel docs:
```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-policy-models.git
# If you've previously done this, move aside the old rules directory
mv ~/code/laa-ccms-opa-policy-models-zips-extracted /tmp/
unzip laa-ccms-opa-policy-models/MeansAssessment.zip -d ~/code/laa-ccms-opa-policy-models-zips-extracted
```

Clone this repository, which is where the resulting markdown goes
```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-means-assessment-markdown
```

## docx2ruletxt

Converts a .docx file, containing OPA rules, into .ruletxt format.

.ruletxt is a format designed to contain all the OPA rule information, but in a simple text-based format, so that it is easier to write tools to process it, and include rules in test cases.

To view a .docx file as .ruletxt:
```
source venv/bin/activate
python docx2ruletxt.py ../laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR\ System\ Rules.docx
```
### Convert all .docx files

Locate the folders for the extracted zip and output repo (adjust these if you put them elsewhere):

```sh
export OPA_REPO_DIR=~/code/laa-ccms-opa-policy-models
export EXTRACTED_MODELS_DIR=~/code/laa-ccms-opa-policy-models-zips-extracted
export OUT_DIR=~/code/laa-ccms-opa-means-assessment-ruletxt
export PYTHON_CMD=~/code/opa_tools/venv/bin/python
export PARSE_PY=~/code/opa_tools/docx2ruletxt.py
```

Get the latest the Word docs:
```sh
cd $OPA_REPO_DIR
git pull
# If you've previously done this, move aside the old rules directory
mv $EXTRACTED_MODELS_DIR /tmp/
unzip MeansAssessment.zip -d $EXTRACTED_MODELS_DIR
```

Convert the Word docs:

```sh
cd $EXTRACTED_MODELS_DIR/MeansAssessment/rules
find . -name "*.docx" -exec sh -c '
  FILE="$1"
  OUT_DIR="$2"
  DIRNAME=$(dirname "$FILE")
  BASENAME=$(basename "$FILE" .docx)
  NEWNAME="${BASENAME// /_}.ruletxt"
  DEST_DIR="$OUT_DIR/$DIRNAME"
  mkdir -p "$DEST_DIR"
  $PYTHON_CMD $PARSE_PY "$FILE" "$DEST_DIR/$NEWNAME" || echo "$FILE"
' sh {} "$OUT_DIR" \;
```

Commit the changes to this repo:
```sh
cd $OUT_DIR
```


## Parse docx

Parses an OPA rule document.

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
export PYTHON_CMD=~/code/opa_tools/venv/bin/python
export PARSE_PY=~/code/opa_tools/parse_docx.py
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
