from lex import *

def main():
    input = "+- */ # Comment! \n >>= = !="
    lexer = Lexer(input)

    token = lexer.getToken()
    while token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()

main()