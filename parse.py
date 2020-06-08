from lex import *
import sys

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.symbols = set() # Variables declared so far
        self.labelsDeclared = set() # Labels declared so far
        self.labelsGotoed = set() # Labels goto'ed so far
        
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() # Initialize current token and next-in-line (peek)

    # Return true if the current token matches  
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # Return true if the next token matches
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # Try to match current token. If not, throw error. Also advances current token
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected" + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances current token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # EOF is handled by lexer


    def abort(self, message):
        sys.exit("Parser Error: " + message)

    
    # Production rules begin here ---

    # program ::= {statement}
    def program(self):
        print("PROGRAM")

        # Skip excess nl
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all statements in program until EOF
        while not self.checkToken(TokenType.EOF):
            self.statement()

        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting GOTO to undeclared label: " + label)

    
    # statement ::= "PRINT" (expression | string) nl
    # etc..
    def statement(self):
        # Check first token to see statement type

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                self.nextToken()
            else:
                self.expression()
        # "IF" comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            # Zero or more statements in body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
        # "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()

            # Zero or more statements in loop body
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()

            # Make sure label does not exist already
            if self.curToken.text in self.labelsDeclared:
                self.abort("Duplicate label: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)
            
            self.match(TokenType.IDENT)
        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.match(TokenType.IDENT)
        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()

            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)

            self.match(TokenType.IDENT)
        # Invalid statement
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        self.nl()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=" ) expression)+
    def comparison(self):
        print("COMPARISON")

        self.expression()
        # Must be at least one comparison operator and expression
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        # But we can have more of course
        while self.isComparisonOperator():
            self.nextToken()
            self.expression()

    # Return true if token is comparison op
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")

        self.term()
        # Can have 0 or more +/- and expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
            self.term()

    # term ::= unary {/ "/" | "*" ) unary}
    def term(self):
        print("TERM")

        self.unary()
        # Can have 0 or more *// and expressions
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        print("UNARY")

        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER):
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure variable exists
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)
            self.nextToken()
        else:
            self.abort("Unexpected token at " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")

        # At least one nl required
        self.match(TokenType.NEWLINE)

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()