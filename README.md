# OPA Tools

A selection of tools for working with OIA (Oracle Intelligent Advisor) or OPA (Oracle Policy Automation) rulebases, which are Word and Excel files, authored with OPM (Oracle Policy Modeling). Read more about the tools and formats below.

## Setup

```sh
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

Ensure you've installed Git Large File Storage, needed by MOJ's rulebase repo:
```sh
brew install git-lfs
# Update system git config
git lfs install
```

Get the rulebase, in the original Word & Excel docs:

```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-means-v23.git
# If you've previously done this, move aside the old rules directory
mv ~/code/laa-ccms-opa-policy-models-zips-extracted /tmp/
unzip laa-ccms-opa-means-v23/MeansAssessment.zip -d ~/code/laa-ccms-opa-policy-models-zips-extracted
```

Clone the ruletxt repository, which is where the resulting ruletxt will be written:

```sh
cd ~/code
git clone git@github.com:ministryofjustice/laa-ccms-opa-means-assessment-ruletxt
```

## docx2ruletxt

Converts a .docx file, containing OPA rules, into .ruletxt format. See below about .ruletxt.

To view a .docx file as .ruletxt:

```sh
source venv/bin/activate
python docx2ruletxt.py ../laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR\ System\ Rules.docx
```

### Convert all .docx files

Locate the folders for the extracted zip and output repo (adjust these if you put them elsewhere):

```sh
export OPA_REPO_DIR=~/code/laa-ccms-opa-means-v23
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
cd $RULETXT_DIR
```

Commit the changes to the repo:

```sh
cd $RULETXT_DIR
git commit -a -m 'Update'
git push
```


## Convert to Python

Converts ruletxt files to Python code.

### Extra setup

1. Get a copy of the attributes, directly from Oracle Policy Modelling:

    In your AWS WorkSpace:
    * Install OPA from: "P:\Install Files\CIS_Install\OPM zips\OPM 23B installer"
    * Download the [rulebase .zip](https://github.com/ministryofjustice/laa-ccms-opa-means-v23/blob/main/MeansAssessment.zip), unzip it, and put the folder into ~\Documents\Oracle Policy Modeling Projects
    * Select "Data" tab, select "Flat view", select "Export"
    * Copy the resulting CSVs (via your Google Drive) to ~/code/opa_tools/

    (To make getting the attributes easier, we should extract these CSVs during the OPA CI using [OPMExport.exe](https://documentation.custhelp.com/euf/assets/devdocs/unversioned/IntelligentAdvisor/en/Content/Guides/Use_Intelligent_Advisor/Command_line_tools/Export_data_model_from_command_line.htm))

2. Compile the parser:

    ```sh
    cd ~/code/opa_tools
    nvm install 16
    nvm use 16
    npm install canopy
    ./node_modules/canopy/bin/canopy ruletxt2python/ruletxt.peg --lang python --output ruletxt2python/ruletxt_parser
    ```

### Run

To convert one file:

```sh
source venv/bin/activate
python ruletxt2python/ruletxt2python.py attributes-2024-07-02-23b.csv ../laa-ccms-opa-means-assessment-ruletxt/Work\ Package\ 1/WP1._\(1-7\).ruletxt
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

## OIA's "docx" files

The docx file contains rules, either in paragraphs or in tables (containing paragraphs).
The rule information is contained in the *text*, paragraph *style* and *table* structure.

[Rules documentation](https://documentation.custhelp.com/euf/assets/devdocs/unversioned/IntelligentAdvisor/en/Content/Guides/Use_Intelligent_Advisor/Use_Policy_Modeling/Work_with_rules/Work_with_rules.htm)

We use the 'docx' python library to parse the docx file, because it's simple.

## If block

This example shows the styles for each paragraph:
```
[OPM-conclusion] the upcoming changes section is visible if
[OPM-level1]     the LAR rules apply to this application and
[OPM-level2]       the client is under 18 or
[OPM-level2]       the client is passported
```

## Tables

This example shows the typical structure and styles:
```
[OPM-conclusion] the name change Funding Code to LAPSO
[OPM-conclusion] "Funding Code" | [OPM-level1] the LAR rules do not apply to this application
[OPM-conclusion] "Lord Chancellor’s Guidance on financial eligibility for certificated work" |	[OPM-Alternativeconclusion] otherwise
```

# Ruletxt format

Ruletxt is a file format designed (with the creation of this repository) to contain all the OPA rule information, but in a simple text-based format. This is useful for a few reasons:

* changes can be tracked with git and diff (whereas Word and Excel are opaque)
* tools for processing ruletxt are easier to write for Ruletxt, than Word & Excel
* test cases (for tools) can include rules
