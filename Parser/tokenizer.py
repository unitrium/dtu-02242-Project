"""Take a string as input and outputs an array of token in the order in which they are read."""
import re                                 # for performing regex expressions

STATEMENTS = [":=", "if", "else", "while", "read", "write", ","]
DECLARATIONS = ["int", "int["]
ARITHMETIC_OPERATORS = ["+", "-", "*", "/", "%"]
RELATIVE_OPERATORS = ["<", ">", "<=", ">=", "==", "!="]
BOOLEAN_OPERATORS = ["&", "|", "!"]

class Scanner:
    # Identifiers --> int a, b etc.
    # Seperators --> {, },
    # Keywords --> if, else, do, od etc.
    # Operators -->  +, -, <, >, ==, != etc.
    tokens = []                               
    source_code = '{int result := 100;}'.split()

    # Loop through each source code word
    for word in source_code:
        if word in '{':
            tokens.append(['START_BLOCK', '{'])

        elif word in ['str', 'int', 'bool']: 
            tokens.append(['DATATYPE', word])
        
        elif re.match("[a-z]", word) or re.match("[A-Z]", word):
            tokens.append(['IDENTIFIER', word])
            if word[len(word) - 1] == ';': 
                tokens.append(['END_OF_STATEMENT', ';'])
        
        elif word in '*-/+%&|!<>' or word in ':=':
            tokens.append(['OPERATOR', word])
        
        elif word in ['WHILE', 'if', 'else', 'read', 'break', 'do', 'od']:
            tokens.append(['KEYWORDS', word])
            
        elif word in '(':
            tokens.append(['BEGIN_STATEMENT', word])
            
        elif word in ')':
            tokens.append(['END_STATEMENT', word])

        elif word in '}':
            tokens.append(['END_BLOCK', '}'])
        
        elif re.match(".[0-9]", word):
            if word[len(word) - 1] == ';': 
                tokens.append(["INTEGER", word[:-1]])
                tokens.append(['END_OF_STATEMENT', ';'])
            else: 
                tokens.append(["INTEGER", word])

    print(tokens) # Outputs the token array