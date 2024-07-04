import pandas as pd

from io import StringIO
import re


def process_attributes_csv(attributes_csv_filepath):
    process_attributes(pd.read_csv(attributes_csv_filepath))

def process_attributes_csv_buffer(attributes_csv_buffer):
    process_attributes(pd.read_csv(StringIO(attributes_csv_buffer)))

def process_attributes(attributes_df):
    global attributes_converter
    global attributes_pattern

    attributes_converter = {}
    for index, row in attributes_df.iterrows():
        root_attribute = row['Attribute Text']
        root_attribute_variable = attribute_root_name_to_variable(root_attribute)
        attributes_converter[root_attribute.lower()] = f'{root_attribute_variable}'
        if row.get('Negative') and isinstance(row['Negative'], str):
            attributes_converter[row['Negative'].rstrip('.')] = f'not {root_attribute_variable}'

    # Sort attributes by length in descending order
    
    for key, value in attributes_converter.items():
        if isinstance(key, float): print(repr(key), repr(value))
    sorted_attributes = sorted(attributes_converter.keys(), key=len, reverse=True)
    # Regex pattern that matches any of the attributes
    attributes_pattern = re.compile('|'.join(re.escape(attr) for attr in sorted_attributes), re.IGNORECASE)

# for tests
def get_attributes_converter():
    return attributes_converter


def identify_attributes(line):
    '''Replaces attribute names in the line with "<attr>". Is greedy.'''
    matched_attributes = []

    def replace_match(match):
        matched_attributes.append(match.group(0))
        return '<attr>'
    
    result_line = attributes_pattern.sub(replace_match, line)
    
    return result_line, matched_attributes


def attribute_root_name_to_variable(attribute_name):
    '''Convert a root attribute name to a variable name
    
    e.g. 'is over 18'
      -> 'is_over_18'
    '''
    # Replace spaces with underscores
    s = attribute_name.replace(' ', '_')
    # Remove all non-alphanumeric characters and underscores
    s = re.sub(r'[^0-9a-zA-Z_]', '', s)
    # Ensure the variable name doesn't start with a digit
    if s and s[0].isdigit():
        s = '_' + s
    return s

def attribute_incl_variants_to_variable(attribute_name_including_variants):
    '''Convert an attribute name (including variants) to a variable name and possibly some logic.
    
    e.g. 'is not over 18'
      -> 'not is_over_18' 
    '''
    # Handle the 'not' keyword and replace other characters
    s = re.sub(r'\bnot\b', 'not ', attribute_name_including_variants)  # Add space after 'not' for proper split
    parts = re.split(r'\s+', s.strip())  # Split by any whitespace
    transformed_parts = ['not' if part == 'not' else re.sub(r'\W+', '_', part) for part in parts]
    return '_'.join(transformed_parts).strip('_')
