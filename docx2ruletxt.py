import os
import sys

import docx


if len(sys.argv) > 1:
    input_filepath = sys.argv[1]
    if os.path.basename(input_filepath).startswith('~$'):
        print(f'Ignoring tempfile created by Word {input_filepath}')
        sys.exit(0)
else:
    print("No input filepath provided")
    sys.exit(1)
print(input_filepath)

f = None
if len(sys.argv) > 2:
    out_filepath = sys.argv[2]
    f = open(out_filepath, 'w')

def print_(header_tag, body):
    padding = ' ' * (max(len('[table-OPM-conclusion]') - len(header_tag) - 2, 0))
    body = body.rstrip()
    if '\n' in body:
        # very rare to see a newline inside a paragraph or table cell.
        # print a symbol, rather than have lines without a header tag
        body = body.replace('\n', '\\n')
    line = f'[{header_tag}] {padding} {body}'
    if f:
        print(line, file=f)
    else:
        print(line)    


def process_paragraph(p, doc_index):
    style = p.style.style_id
    indent = 0
    if style.startswith('OPM-level'):
        indent = int(style.split('OPM-level')[1])
    print_(style, '    ' * (indent - 1)+ f'{p.text}')

def process_table(table, doc_index):
    for row_index, r in enumerate(table.rows):
        row_cells = tuple(c for c in r.cells)

        if row_index == 0 and row_cells[0].paragraphs[0].style.style_id != 'OPM-conclusion':
            # this table isn't a rule
            return process_nonrule_table(table, doc_index)
        
        # hack to fix one table in 'Work Package 3/WP3 Calculation 30 -37.docx'
        if len(row_cells) == 3 and row_cells[0].text == row_cells[1].text:
            row_cells = (row_cells[0], row_cells[2])

        if len(row_cells) != 2:
            print_('ERROR', f'table row has too many cells {doc_index=} {row_index=} {len(row_cells)=}')
            breakpoint()
            continue
        
        cell1_style = row_cells[1].paragraphs[0].style.style_id    
        # We're only interested in the styles in the 2nd column - the 1st column is always OPM-conclusion
        if row_index == 0:
            # In Word, this first row is a single merged cell, but it comes through to here as two duplicate cells
            print_(f'table-{cell1_style}', f'{row_cells[1].paragraphs[0].text}')
        else:
            for i, paragraph in enumerate(row_cells[1].paragraphs):
                if i == 0:
                    print_(f'table-{cell1_style}', f'{row_cells[0].text} | [1] {paragraph.text}')
                else:
                    indent = 0
                    if paragraph.style.style_id.startswith('OPM-level'):
                        indent = int(paragraph.style.style_id.split('OPM-level')[1])
                    print_('table-cell-continued', f'  | [{indent}] ' + '    ' * (indent - 1) + f'{paragraph.text}')

    # print_('table-end', '')

def process_nonrule_table(table, doc_index):
    for row_index, r in enumerate(table.rows):
        row_cells = tuple(c for c in r.cells)
        print_('nonrule-table', ' | '.join((cell.text for cell in row_cells)))

document = docx.Document(input_filepath)
for doc_index, doc_object in enumerate(document.iter_inner_content()):
    if isinstance(doc_object, docx.text.paragraph.Paragraph):
        process_paragraph(doc_object, doc_index)
    elif isinstance(doc_object, docx.table.Table):
        process_table(doc_object, doc_index)
    else:
        print_('ERROR', f'Unhandled doc object: {type(doc_object)}')
