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
			varname = self.la
			self.match('IDENTIFIER')
			self.match('=')
			self.st[varname]=self.expr()
		elif self.la == 'print':
			self.match('print')
			print(self.expr())
		else:
			raise ParseError('Stmt Error')
	
	def expr(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE':
			t = self.term()
			tt = self.term_tail()
			if tt is None:
				return t
			if tt[0] == 'or':
				return t or tt[1]
			if tt[0] == 'and':
				return t and tt[1]
		else:
			ParseError('Expr Error')
	
	def term_tail(self):
		if self.la == 'and' or self.la == 'or':
			aoop = self.aoop()
			t = self.term()
			tt = self.term_tail()
			if tt is None:
				return aoop, t
			if tt[0] == 'or':
				return aoop, t or tt[1]
			if tt[0] == 'and':
				return aoop, t and tt[1]
		elif self.la in ('IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('Term_tail Error')
	
	def term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'TRUE' or self.la == 'FALSE' or self.la == 'not':
			f = self.factor()
			ft = self.factor_tail()
		else:
			raise ParseError('Term Error')
	
	def factor_tail(self):
		if self.la == 'not':
			nop = self.nop()
			f = self.factor()
			ft = self.factor_tail()
			if ft is None:
				return nop, f
			if ft[0] == 'not':
				return nop, f or ft[1]
		elif self.la in ('and','or','IDENTIFIER','print',None,')'):
			return
		else:
			raise ParseError('Factor_tail Error')
	
	def factor(self):
		if self.la == '(':
			self.match('(')
			return '('
			expr = self.expr()
			self.match(')')
			return ')'
			return expr
		elif self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
		elif self.la == 'TRUE':
			self.match('TRUE')
			return 'True'
		elif self.la == 'FALSE':
			self.match('FALSE')
			return 'False'
		elif self.la in ('not','and','or',None,')','print'):
			return
		else:
			raise ParseError('Factor Error')
	
	def aoop(self):
		if self.la == 'and':
			self.match('and')
			return 'and'
		elif self.la == 'or':
			self.match('or')
			return 'or'
		else:
			raise ParseError('and/or Error')
	
	def nop(self):
		if self.la == 'not':
			self.match('not')
			return 'not'
		else:
			raise ParseError('Not Error')
	

parser = MyParser()
with open('data.txt') as fp:
	try:
		parser.parse(fp)
	except ParseError as perr:
		print(perr)
