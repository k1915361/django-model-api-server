import os 

def get_file_extension(file_path):
    """Gets the file extension (without the leading dot)."""
    _, ext = os.path.splitext(file_path)
    if ext:  
        return ext.lower()
    return ""

s = get_file_extension('a.b.c.D')
assert s == '.d'

s = get_file_extension('ABC.XYZ.D')
assert s == '.d'

from enum import Enum

class ActionSet(Enum):
    CLEANING = 1
    ANALYSIS = 2
    ENRICHMENT = 3
    CURATION = 4
    DATA_BALANCING = 5
    EXPLAINABLE_AI = 6

print(ActionSet(2).value)
print(ActionSet(2).name)
print(ActionSet.ANALYSIS.value)
print(ActionSet.ANALYSIS.name)