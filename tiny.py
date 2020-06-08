from lex import *

def main():
    input = "IF +-2344 foo*THEN/"
    lexer = Lexer(input)

    token = lexer.getToken()
    while token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()

main()