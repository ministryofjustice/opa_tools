# OPA Tools

A selection of tools for working with OPA (Oracle Policy Automation) rulebases.

## Setup

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Get the OPA rulebase, in the original Word & Excel docs:

```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-policy-models.git
# If you've previously done this, move aside the old rules directory
mv ~/code/laa-ccms-opa-policy-models-zips-extracted /tmp/
unzip laa-ccms-opa-policy-models/MeansAssessment.zip -d ~/code/laa-ccms-opa-policy-models-zips-extracted
```

Clone the ruletxt repository, which is where the resulting ruletxt will be written:

```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-means-assessment-ruletxt
```

## docx2ruletxt

Converts a .docx file, containing OPA rules, into .ruletxt format.

.ruletxt is a format designed to contain all the OPA rule information, but in a simple text-based format, so that it is easier to write tools to process it, and include rules in test cases.

To view a .docx file as .ruletxt:

```sh
source venv/bin/activate
python docx2ruletxt.py ../laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR\ System\ Rules.docx
```

### Convert all .docx files

Locate the folders for the extracted zip and output repo (adjust these if you put them elsewhere):

```sh
export OPA_REPO_DIR=~/code/laa-ccms-opa-policy-models
export EXTRACTED_MODELS_DIR=~/code/laa-ccms-opa-policy-models-zips-extracted
export RULETXT_DIR=~/code/laa-ccms-opa-means-assessment-ruletxt
export PYTHON_CMD=~/code/opa_tools/venv/bin/python
export DOCX2RULETXT=~/code/opa_tools/docx2ruletxt.py
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
  RULETXT_DIR="$2"
  DIRNAME=$(dirname "$FILE")
  BASENAME=$(basename "$FILE" .docx)
  NEWNAME="${BASENAME// /_}.ruletxt"
  DEST_DIR="$RULETXT_DIR/$DIRNAME"
  mkdir -p "$DEST_DIR"
  $PYTHON_CMD $DOCX2RULETXT "$FILE" "$DEST_DIR/$NEWNAME" || echo "$FILE"
' sh {} "$RULETXT_DIR" \;
```

Commit the changes to the repo:

```sh
cd $RULETXT_DIR
git commit -a -m 'Update'
git push
```


## Convert to Python

Converts ruletxt files to Python code.

### Run

To convert one file:

```sh
source venv/bin/activate
python ruletxt2python/ruletxt2python.py 2023_08_28_opa_means_assessment_all_attributes.csv ../laa-ccms-opa-means-assessment-ruletxt/LAR/LAR_System_Rules.ruletxt
```

### Convert all files

Locate the folders (adjust these if you put them elsewhere):

```sh
export RULETXT_DIR=~/code/laa-ccms-opa-means-assessment-ruletxt
export RULEPYTHON_DIR=~/code/laa-ccms-opa-means-assessment-python
export PYTHON_CMD=~/code/opa_tools/venv/bin/python
export DOCX2RULETXT=~/code/opa_tools/docx2ruletxt.py
```

Get the latest the ruletxt docs:
```sh
cd $RULETXT_DIR
git pull
```

Convert:

```sh
cd $RULETXT_DIR
find . -name "*.ruletxt" -exec sh -c '
  FILE="$1"
  RULEPYTHON_DIR="$2"
  DIRNAME=$(dirname "$FILE")
  BASENAME=$(basename "$FILE" .docx)
  NEWNAME="${BASENAME// /_}.py"
  DEST_DIR="$RULEPYTHON_DIR/$DIRNAME"
  mkdir -p "$DEST_DIR"
  $PYTHON_CMD $DOCX2RULETXT "$FILE" "$DEST_DIR/$NEWNAME" || echo "$FILE"
' sh {} "$RULEPYTHON_DIR" \;
```

Commit the changes to the repo:

```sh
cd $RULEPYTHON_DIR
```

### Tests

```
source venv/bin/activate
pytest
```

## Importer

Imports a CSV into a sqlite database. It's useful to import a CSV of OPA attributes, so that you can then use SQL to query it.

```
source venv/bin/activate
python import.py
```
