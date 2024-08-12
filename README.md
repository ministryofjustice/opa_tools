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
python docx2ruletxt.py -i ../laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR\ System\ Rules.docx
```

### Convert all .docx files

Get the latest the Zip and extract to Word docs:
```sh
cd ~/code/laa-ccms-opa-means-v23
git pull
# If you've previously done this, move aside the old extracted model
mv ../laa-ccms-opa-means-v23-extracted /tmp/
unzip MeansAssessment.zip -d ../laa-ccms-opa-means-v23-extracted
```

Convert the Word docs to Ruletxt
```sh
# If you've previously done this, delete the old ruletxt files
rm -rf ../laa-ccms-opa-means-assessment-ruletxt/*
python docx2ruletxt.py -d ../laa-ccms-opa-means-v23-extracted/MeansAssessment/Rules -o ../laa-ccms-opa-means-assessment-ruletxt
```

Commit the changes to the repo:
```sh
cd ~/code/laa-ccms-opa-means-assessment-ruletxt
git commit -a -m 'Update'
git push
```

### Convert the full git history of .docx files

Get the latest input repo, with the zipped OPA rules:
```sh
cd ~/code/laa-ccms-opa-means-v23
git pull
```

Prepare an output repo:
```sh
cd ~/code
mkdir laa-ccms-opa-means-ruletxt
cd laa-ccms-opa-means-ruletxt
git init
```

Convert all git commits:
```sh
source venv/bin/activate
ruletxt2python/convert_repo.sh ~/code/laa-ccms-opa-means-v23 MeansAssessment.zip ../laa-ccms-opa-means-ruletxt
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

    This generates ruletxt2python/ruletxt_parser.py

### Run

To convert one file:

```sh
source venv/bin/activate
python ruletxt2python/ruletxt2python.py attributes-2024-07-02-23b.csv ../laa-ccms-opa-means-assessment-ruletxt/Work\ Package\ 1/WP1._\(1-7\).ruletxt
```

### About the parser

The 'grammar' of ruletxt files is described in `ruletxt.peg`, using standard Parsing Expression Grammar (PEG) notation. Each 'rule' in the grammar is a mix of regexes and other rules, so you can see it is recursive.

The 'parser' `ruletxt_parser.py` is generated from the PEG, using Canopy.

The parser first does the 'lexing' - it reads the text in the ruletxt file, identifying snippets of text as grammar rules, and represents each rule and snippet of text as a node in a tree - this is the 'parsing tree'. For example, OID text `client's name <> "bob"` is identified as an attribute `client's income`, comparator `<` and constant `12000`. These are three nodes, with a parent node 'Expression'.

We also supply the parser with 'actions' in `parser_actions.Actions`. These are python functions for each grammar rule, for converting the parsing tree, in this case into python code. In our example, they'll convert `client's name` to python variable `clients_name`, `<>` to `!=`. It does it recursively starting with the top node 'Document', building up the whole python file, equivalent to the ruletxt input.

#### Why we chose Canopy

We followed [Gabriele Tomassetti's guide to Parsing In Python](https://tomassetti.me/parsing-in-python/) as a basis.

* Tomassetti advises to use a parsing library, unless you have a special need to manually write a parser](https://tomassetti.me/parsing-in-python/), because it's easier to reason about parsing by writing the grammar, and letting a compiler or library do the parsing bit. 
* Ruletxt is parseable with a standard PEG/CFL parser:
    * OIA's logic is nestable (e.g. `(a<b and (b<d or e<>f))`), so we need the recursion / tree structure provided by a Context Free Language (CFL) (rather than a regular language)
    * we introduced brackets into ruletxt to ensure that the parser didn't need to keep track of the recursion level. For example, the parser encountering [OPM-level2], or indent of 8, doesn't know if it is recursing into a nested block or not, unless it knows the previous level or indent. (This is why most programming languages have brackets, and Python causes a bit of a headache for its parser by using spaces)
* Canopy has the advantage of producing parser code in Java, Python or Ruby, giving us options. And it seemed simple enough to get working. We didn't look very hard at other parser libraries, but since it uses standard PEG grammar, it wouldn't be hard to switch to another.

### Parser development tips:

If you get an exception in ruletxt_parser.py, then you can see how it has interpreted the text by printing `self._cache`. For example:
```py
(Pdb) pp(self._cache)
defaultdict(<class 'dict'>,
            {'AllEtc': {45: (<object object at 0x1003f8df0>, 45)},
             'OPMLevel': {32: (<ruletxt2python.ruletxt_parser.TreeNode object at 0x101986450>,
                               44),
                          45: (<object object at 0x1003f8df0>, 45)},
```
This shows it has identified the grammar rule named 'OPMLevel' between characters 32 and 44 of the input text, and created a TreeNode. You can see the text by printing that TreeNode, or with a slice of the input:
```py
(Pdb) self._cache['OPMLevel'][32][0].text
'[OPM-level1]'
(Pdb) self._input[32:44]
'[OPM-level1]'
```
There are also objects like `(<object object at 0x1003f8df0>, 45))` which are placeholders. During the parsing these each replaced with a TreeNode or not.

```
E   RecursionError: maximum recursion depth exceeded
!!! Recursion detected (same locals & position)
```
This RecursionError in the parser is due to recursing back to the same grammar rule at the same offset. For example, in an Expression we find a sub-Expression:
e.g.
```py
ruletxt2python/ruletxt_parser.py:407: in _read_Expression
    address2 = self._read_Comparison()
ruletxt2python/ruletxt_parser.py:577: in _read_Comparison
    address1 = self._read_Expression()
ruletxt2python/ruletxt_parser.py:407: in _read_Expression
    address2 = self._read_Comparison()
```
This may be what was intended in the Grammar, but the parser doesn't like them both starting in the same place, because they appear the same in the result cache.

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
