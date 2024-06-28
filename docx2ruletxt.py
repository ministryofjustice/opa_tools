import os
import sys

import docx


#input_filepath = os.path.expanduser("~/code/laa-ccms-opa-policy-models-zips-extracted/MeansAssessment/Rules/LAR/LAR System Rules.docx")
if len(sys.argv) > 1:
    input_filepath = sys.argv[1]
else:
    print("No input filepath provided")
    sys.exit(1)

if len(sys.argv) > 2:
    out_filepath = sys.argv[2]
    f = open(out_filepath, 'w')
    sys.stdout = f

def print_(header_tag, body):
    padding = ' ' * (max(len('[OPM-conclusion]') - len(header_tag) - 2, 0))
    if '\n' in body:
        breakpoint()
    print(f'[{header_tag}] {padding} {body}')

def process_paragraph(p, doc_index):
    style = p.style.style_id
    indent = 0
    if style.startswith('OPM-level'):
        indent = int(style.split('OPM-level')[1])
    print_(style, '    '*indent + f'{p.text}')

def parse_table(table, doc_index):
    for row_index, r in enumerate(table.rows):
        row_cells = tuple(c for c in r.cells)
        if len(row_cells) != 2:
            print_('ERROR', f'table row has too many cells {doc_index=} {row_index=} {len(row_cells)=}')
            return None
        
        # cell0_style = row_cells[0].paragraphs[0].style.style_id
        cell1_style = row_cells[1].paragraphs[0].style.style_id    
        # We're only interested in the styles in the 2nd column - the 1st column is always OPM-conclusion
        if row_index == 0:
            if cell1_style != 'OPM-conclusion':
                print_('ERROR', f'table first row should be style: OPM-conclusion {doc_index=} {row_index=} {cell1_style=}')
                return None
            # In Word, this first row is a single merged cell, but it comes through to here as two duplicate cells
            print_(f'table-{cell1_style}', f'{row_cells[1].paragraphs[0].text}')
        else:
            print_(f'table-{cell1_style}', f'{row_cells[0].paragraphs[0].text} | {row_cells[1].paragraphs[0].text}')

document = docx.Document(input_filepath)
for doc_index, doc_object in enumerate(document.iter_inner_content()):
    if isinstance(doc_object, docx.text.paragraph.Paragraph):
        process_paragraph(doc_object, doc_index)
    elif isinstance(doc_object, docx.table.Table):
        parse_table(doc_object, doc_index)
        print('\n')
    else:
        print_('ERROR', f'Unhandled doc object: {type(doc_object)}')


# for table_index, table in enumerate(document.tables):
#     # print(f'Table {table_index}:')
    
    