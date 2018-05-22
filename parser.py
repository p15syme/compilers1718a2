"""
LL(1) Grammar:

<Program> -> Stmt_list #

Stmt_list -> Stmt Stmt_list
          |.
Stmt -> id = Expr 
     | print Expr.
Expr -> Term Term_tail.
Stmt_list -> Stmt Stmt_list
          |.
Stmt -> id = Expr 
     | print Expr.
Expr -> Term Term_tail.
Term_tail -> Aoop Term Term_tail
          |.
Term -> Factor Factor_tail.
Factor_tail -> Nop Factor Factor_tail 
            |.
Factor -> (Expr)
       | id
       | tf01.

Aoop -> and
        | or.
Nop -> not.

FIRST sets:
------------
Stmt_list: id print
Stmt: id print
Expr: (Expr) id tf01
Term_tail: and or
Term: (Expr) id tf01
Factor_tail: not 
Factor: (Expr) id tf01
Aoop: and or 
Nop: not

FOLLOW sets:
------------
Stmt_list: 
Stmt: id print
Expr: id print
Term_tail: id print
Term: and or id print
Factor_tail: and or id print
Factor: not and or id print
Aoop: (Expr) id tf01
Nop: (Expr) id tf01
"""

import plex

class ParseError(Exception):
	pass
	
	
class MyParser:

	def __init__(self):
		self.st = {}

	def create_scanner(self,fp):
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		name = letter + plex.Rep(letter|digit)
		keyword = plex.Str('print')

		aoop = plex.Str('and','or')
		nop = plex.Str('not')

		f0 = plex.NoCase(plex.Str('false','f','0'))
		t1 = plex.NoCase(plex.Str('true','t','1'))

		telestis = plex.Str('=')
		parenthesis = plex.Any('()')

		space = plex.Rep1(plex.Any(' \n\t'))

		
		lexicon = plex.Lexicon([
			(keyword,plex.TEXT),
			(aoop,plex.TEXT),
			(nop,plex.TEXT),
			(f0,'FALSE'),
			(t1,'TRUE'),
			(name,'IDENTIFIER'),
			(space,plex.IGNORE),
			(parenthesis,plex.TEXT),
			(telestis,plex.TEXT)
			])
			
		self.scanner = plex.Scanner(lexicon,fp)
		self.la, self.val = self.next_token()

	def parse(self,fp):
		self.create_scanner(fp)
		self.stmt_list()

	def match(self,token):
		if self.la == token:
			self.la, self.val = self.next_token()
		else:
			raise ParseError('Match Error')
	
	def next_token(self):
		return self.scanner.read()
	
	def stmt_list(self):
		if self.la == 'IDENTIFIER' or self.la == 'print':
			self.stmt()
			self.stmt_list()
		elif self.la is None:
			return
		else:
			raise ParseError('Stmt_list Error')
	
	def stmt(self):
		if self.la == 'IDENTIFIER' or self.la == '=':
			self.match('IDENTIFIER')
			self.match('=')
			self.expr()
		elif self.la == 'print':
			self.match('print')
			self.expr()
		else:
			raise ParseError('Stmt Error')
	
	def expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE':
			self.term()
			self.term_tail()
		else:
			ParseError('Expr Error')
	
	def term_tail(self):
		if self.la == 'and' or self.la == 'or':
			self.aoop()
			self.term()
			self.term_tail()
		elif self.la in ('IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('Term_tail Error')
	
	def term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE' or self.la == 'not':
			self.factor()
			self.factor_tail()
		else:
			raise ParseError('Term Error')
	
	def factor_tail(self):
		if self.la == 'not':
			self.nop()
			self.factor()
			self.factor_tail()
		elif self.la in ('and','or','IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('Factor_tail Error')
	
	def factor(self):
		if self.la == '(':
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
		elif self.la == 'TRUE':
			self.match('TRUE')
		elif self.la == 'FALSE':
			self.match('FALSE')
		elif self.la in ('not','and','or',None,')','print'):
			return
		else:
			raise ParseError('Factor Error')
	
	def aoop(self):
		if self.la == 'and':
			self.match('and')
		elif self.la == 'or':
			self.match('or')
		else:
			raise ParseError('and/or Error')
	
	def nop(self):
		if self.la == 'not':
			self.match('not')
		else:
			raise ParseError('Not Error')
	

parser = MyParser()
with open('data.txt') as fp:
	try:
		parser.parse(fp)
	except ParseError as perr:
		print(perr)
