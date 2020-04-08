start: sccd;

sccd: diagram INDENT (top)? element+ (bottom)? DEDENT;

@element: (inport | outport | class);

inport: INPORT LPAR nameattr RPAR NEWLINE;
outport: OUTPORT LPAR nameattr RPAR NEWLINE;

nameattr: NAMEATTR ASSIGN string;
defaultattr: DEFAULTATTR ASSIGN boolean;
classattr: CLASSATTR ASSIGN string;

class: CLASS LPAR classdefattrs RPAR
		( (COLON NEWLINE INDENT classelement+ DEDENT) | NEWLINE);

classdefattrs: classdefattr (COMMA classdefattr)*;

classdefattr: nameattr | defaultattr;

@classelement: inport | outport | association | inheritance | aggregation | composition |
				attribute | constructor | destructor | method | statemachine;

aggregation: AGGREGATION LPAR aggregattrs RPAR NEWLINE;
aggregattrs: relattr (COMMA relattr)*;

composition: COMPOSITION LPAR compattrs RPAR NEWLINE;
compattrs: relattr (COMMA relattr)*;

@relattr: classattr | minattr | maxattr;
minattr: MIN ASSIGN integer;
maxattr: MAX ASSIGN integer;

association: ASSOCIATION LPAR assocattrs RPAR NEWLINE;
assocattrs: assocattr (COMMA assocattr)*;
assocattr: nameattr | relattr;

inheritance: INHERITANCE LPAR inherattrs RPAR NEWLINE;
inherattrs: inherattr (COMMA inherattr)*;
inherattr: priorityattr | classattr;
priorityattr: PRIORITYATTR ASSIGN integer;

attribute: ATTRIBUTE LPAR attributeattrs RPAR NEWLINE;
attributeattrs: attributeattr (COMMA attributeattr)*;
attributeattr: nameattr | defaultvalueattr | typenameattr;
defaultvalueattr: DEFAULTATTR ASSIGN string;
typenameattr: TYPEATTR ASSIGN string;

diagram: DIAGRAM (NEWLINE)+;
DIAGRAM: 'Diagram\([^\)]*\):'
{
	start: 'Diagram\(' attrs '\)' ':';
	@attr: (attrname|attrauthor|attrdescription);
	@attrs:  attr (',' attr)*;
	attrname: ATTRNAME '=' string;
	attrauthor: ATTRAUTHOR '=' string;
	attrdescription: ATTRDESCRIPTION '=' string;

	ATTRNAME: 'name';
	ATTRAUTHOR: 'author';
	ATTRDESCRIPTION: 'description';

	string: (STRVALUE|LONG_STRVALUE) string? ;
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
		(%newline)
		;
	WS: '[\t \f\n]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};

top: TOP BODY NEWLINE;
bottom: BOTTOM BODY;
constructor: CONSTRUCTOR body NEWLINE;
destructor: DESTRUCTOR body NEWLINE;
method: METHOD body NEWLINE;

statemachine: STATEMACHINE (NEWLINE |
	(COLON NEWLINE INDENT (state | orthogonal | pseudostate | transition)+ DEDENT));

@state_element: state | orthogonal | pseudostate | transition | onenter | onexit;

onenter: ONENTER BODY NEWLINE;
onexit: ONEXIT BODY NEWLINE;

state: STATE LPAR statename RPAR (NEWLINE |
	(COLON NEWLINE INDENT state_element+ DEDENT));
orthogonal: ORTHOGONAL LPAR statename RPAR (NEWLINE |
	(COLON NEWLINE INDENT state_element+ DEDENT));
@pseudostate: (initial | final | history) NEWLINE;
initial: INITIAL ASSIGN statename;
final: FINAL ASSIGN statename;
history: HISTORY ASSIGN statename;
statename: string;

transition: TRANSITION LPAR transitionattrs RPAR (NEWLINE |
	(COLON NEWLINE INDENT event? guard? raise* actions? DEDENT));

transitionattrs: transitionattr (COMMA transitionattr)*;
transitionattr: (portattr | targetattr | afterattr);
portattr: PORTATTR ASSIGN string;
targetattr: TARGETATTR ASSIGN string;
afterattr: AFTERATTR;

AFTERATTR: 'after\(.+\)'
{
	start: AFTER LPAR expression RPAR;

	funccall_expr: (expression '->')? functionname LPAR arguments? RPAR;
	functionname: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;


	arguments: argument (COMMA argument)*;
	argument: (argumentname ASSIGN)? expression;
	argumentname: name;

	expression: nav_expr | atomvalue | tuple | vector | dict |
		unopexpr | binopexpr | funccall_expr | selection;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	@unopexpr: parexpr | notexpr | minusexpr;
	parexpr: LPAR expression RPAR;
	notexpr: NOT expression;
	minusexpr: MINUS expression;

	@binopexpr: selection | andexpr | orexpr | lthanexpr | leqthanexpr |
				gthanexpr | geqthanexpr | equalsexpr | nequalsexpr |
				multexpr | divexpr | modexpr | subtractionexpr | sumexpr;

	dict: LSQBR NEWLINE? dictitems NEWLINE? RSQBR;
	dictitems: dictitem (COMMA NEWLINE? dictitem)*;
	dictitem: expression COLON expression;

	vector: LSQBR NEWLINE? (vectoritems NEWLINE?)? RSQBR;
	vectoritems: vectoritem (COMMA NEWLINE? vectoritem)*;
	vectoritem: expression;

	tuple: LPAR tuplearg (COMMA tuplearg)+ RPAR;
	tuplearg: expression;
	selection: expression LSQBR expression RSQBR;
	andexpr: expression LAND expression;
	orexpr: expression LOR expression;
	lthanexpr: expression LTHAN expression;
	leqthanexpr: expression LEQTHAN expression;
	gthanexpr: expression GTHAN expression;
	geqthanexpr: expression GEQTHAN expression;
	equalsexpr: expression EQUALS expression;
	nequalsexpr: expression NEQUALS expression;
	subtractionexpr: expression MINUS expression;
	sumexpr: expression PLUS expression;
	multexpr: expression MULT expression;
	divexpr: expression DIV expression;
	modexpr: expression MOD expression;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			NOT: 'not';
			TRUE: 'True';
			FALSE: 'False';
			LAND: 'and';
			LOR: 'or';
			AFTER: 'after';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;
	
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	MULT: '\*';
	DIV: '/';
	POTENCY: '@\d';
	LTHAN: '<';
	LEQTHAN: '<=';
	GTHAN: '>';
	GEQTHAN: '>=';
	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';
	EQUALS: '==';
	NEQUALS: '!=';
	PLUS: '\+';
	MINUS: '-';
	MOD: '%';
	LSQBR: '\[';
	RSQBR: '\]';

	LBR: '\{';
	RBR: '\}';

	NEWLINE: '(\r?\n[\t ]*)+'
		(%newline)
		;

	WS: '[\t \f]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};


event: EVENT NEWLINE;
EVENT: 'event\ =\ [^\(]+\([^\)]*\)'
{
	start: EVENT ASSIGN namevalue LPAR formalparameters? RPAR;
	formalparameters: formalparameter (COMMA formalparameter)*;
	formalparameter: namevalue COLON nav_expr (ASSIGN defaultvalue)?;
	namevalue: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;

	defaultvalue: atomvalue;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9\-]*(?!r?"|r?\')'
		(%unless
			EVENT: 'event';
			TRUE: 'True';
			FALSE: 'False';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;

	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';

	WS: '[\t \f\n]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};

guard: GUARD NEWLINE;
GUARD: 'guard\ =\ \{[^\}]*\}'
{
	start: GUARD ASSIGN LBR expression RBR;

	funccall_expr: (expression '->')? functionname LPAR arguments? RPAR;
	functionname: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;


	arguments: argument (COMMA argument)*;
	argument: (argumentname ASSIGN)? expression;
	argumentname: name;

	expression: nav_expr | atomvalue | tuple | vector | dict |
		unopexpr | binopexpr | funccall_expr | selection;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	@unopexpr: parexpr | notexpr | minusexpr;
	parexpr: LPAR expression RPAR;
	notexpr: NOT expression;
	minusexpr: MINUS expression;

	@binopexpr: selection | andexpr | orexpr | lthanexpr | leqthanexpr |
				gthanexpr | geqthanexpr | equalsexpr | nequalsexpr |
				multexpr | divexpr | modexpr | subtractionexpr | sumexpr;

	dict: LSQBR NEWLINE? dictitems NEWLINE? RSQBR;
	dictitems: dictitem (COMMA NEWLINE? dictitem)*;
	dictitem: expression COLON expression;

	vector: LSQBR NEWLINE? (vectoritems NEWLINE?)? RSQBR;
	vectoritems: vectoritem (COMMA NEWLINE? vectoritem)*;
	vectoritem: expression;

	tuple: LPAR tuplearg (COMMA tuplearg)+ RPAR;
	tuplearg: expression;
	selection: expression LSQBR expression RSQBR;
	andexpr: expression LAND expression;
	orexpr: expression LOR expression;
	lthanexpr: expression LTHAN expression;
	leqthanexpr: expression LEQTHAN expression;
	gthanexpr: expression GTHAN expression;
	geqthanexpr: expression GEQTHAN expression;
	equalsexpr: expression EQUALS expression;
	nequalsexpr: expression NEQUALS expression;
	subtractionexpr: expression MINUS expression;
	sumexpr: expression PLUS expression;
	multexpr: expression MULT expression;
	divexpr: expression DIV expression;
	modexpr: expression MOD expression;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			NOT: 'not';
			TRUE: 'True';
			FALSE: 'False';
			LAND: 'and';
			LOR: 'or';
			GUARD: 'guard';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;
	
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	MULT: '\*';
	DIV: '/';
	POTENCY: '@\d';
	LTHAN: '<';
	LEQTHAN: '<=';
	GTHAN: '>';
	GEQTHAN: '>=';
	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';
	EQUALS: '==';
	NEQUALS: '!=';
	PLUS: '\+';
	MINUS: '-';
	MOD: '%';
	LSQBR: '\[';
	RSQBR: '\]';

	LBR: '\{';
	RBR: '\}';

	NEWLINE: '(\r?\n[\t ]*)+'
		(%newline)
		;

	WS: '[\t \f]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};

raise: RAISE NEWLINE;
RAISE: 'raise\ \+=\ \{[^\}]*\}'
{
	start: RAISE PLUS ASSIGN LBR scopeattr? targetattr? funccall_expr RBR;

	scopeattr: SCOPE ASSIGN expression COMMA;
	targetattr: TARGET ASSIGN expression COMMA;

	funccall_expr: functionname LPAR arguments? RPAR;
	functionname: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;

	arguments: argument (COMMA argument)*;
	argument: (argumentname ASSIGN)? expression;
	argumentname: name;

	expression: nav_expr | atomvalue | tuple | vector | dict |
		unopexpr | binopexpr | funccall_expr | selection;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	@unopexpr: parexpr | notexpr | minusexpr;
	parexpr: LPAR expression RPAR;
	notexpr: NOT expression;
	minusexpr: MINUS expression;

	@binopexpr: selection | andexpr | orexpr | lthanexpr | leqthanexpr |
				gthanexpr | geqthanexpr | equalsexpr | nequalsexpr |
				multexpr | divexpr | modexpr | subtractionexpr | sumexpr;

	dict: LSQBR NEWLINE? dictitems NEWLINE? RSQBR;
	dictitems: dictitem (COMMA NEWLINE? dictitem)*;
	dictitem: expression COLON expression;

	vector: LSQBR NEWLINE? (vectoritems NEWLINE?)? RSQBR;
	vectoritems: vectoritem (COMMA NEWLINE? vectoritem)*;
	vectoritem: expression;

	tuple: LPAR tuplearg (COMMA tuplearg)+ RPAR;
	tuplearg: expression;
	selection: expression LSQBR expression RSQBR;
	andexpr: expression LAND expression;
	orexpr: expression LOR expression;
	lthanexpr: expression LTHAN expression;
	leqthanexpr: expression LEQTHAN expression;
	gthanexpr: expression GTHAN expression;
	geqthanexpr: expression GEQTHAN expression;
	equalsexpr: expression EQUALS expression;
	nequalsexpr: expression NEQUALS expression;
	subtractionexpr: expression MINUS expression;
	sumexpr: expression PLUS expression;
	multexpr: expression MULT expression;
	divexpr: expression DIV expression;
	modexpr: expression MOD expression;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			NOT: 'not';
			TRUE: 'True';
			FALSE: 'False';
			LAND: 'and';
			LOR: 'or';
			RAISE: 'raise';
			SCOPE: 'scope';
			TARGET: 'target';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;
	
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	MULT: '\*';
	DIV: '/';
	POTENCY: '@\d';
	LTHAN: '<';
	LEQTHAN: '<=';
	GTHAN: '>';
	GEQTHAN: '>=';
	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';
	EQUALS: '==';
	NEQUALS: '!=';
	PLUS: '\+';
	MINUS: '-';
	MOD: '%';
	LSQBR: '\[';
	RSQBR: '\]';

	LBR: '\{';
	RBR: '\}';

	NEWLINE: '(\r?\n[\t ]*)+'
		(%newline)
		;

	WS: '[\t \f]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};


actions: ACTIONS body NEWLINE;

CONSTRUCTOR: 'Constructor(\([^\)]*\))?'
{
	start: CONSTRUCTOR (LPAR formalparameters RPAR)?;
	formalparameters: formalparameter (COMMA formalparameter)*;
	formalparameter: namevalue (COLON nav_expr)?(ASSIGN defaultvalue)?;
	namevalue: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;

	defaultvalue: atomvalue;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			TRUE: 'True';
			FALSE: 'False';
			CONSTRUCTOR: 'Constructor';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;
	
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';

	WS: '[\t \f\n]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};

METHOD: 'Method [^\(]*\([^\)]*\)'
{
	start: METHOD methodname LPAR formalparameters? RPAR;
	methodname: name;
	formalparameters: formalparameter (COMMA formalparameter)*;
	formalparameter: namevalue (COLON nav_expr)?(ASSIGN defaultvalue)?;
	namevalue: name;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;

	defaultvalue: atomvalue;

	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			TRUE: 'True';
			FALSE: 'False';
			METHOD: 'Method';
			SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;
	
	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	ASSIGN: '=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';

	WS: '[\t \f\n]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
};

body: BODY;
BODY: '\{[^\}]*\}'
{
	start: LBR NEWLINE? statement* RBR;
	@statement: import | funccall_stm | decl_stm |
	assignment | plusassign | minusassign | while_stm
	| ifelse_stm | break_stm | continue_stm | return_stm;

	decl_stm: nav_expr decl_name (ASSIGN expression)? NEWLINE;
	decl_name: name;

	return_stm: RETURN (expression)? NEWLINE;

	ifelse_stm: IF expression COLON NEWLINE
						statementbody
					 (ELSE COLON NEWLINE
						statementbody
					)? END NEWLINE
				;

	while_stm: WHILE expression COLON NEWLINE statementbody END NEWLINE;
	statementbody:  statement+;

	break_stm: BREAK NEWLINE;
	continue_stm: CONTINUE NEWLINE;

	import: (FROM fromname)? IMPORT importname (AS asname)? NEWLINE;
	fromname: dotted_name;
	importname: dotted_name | MULT;
	asname: name;

	funccall_stm: (expression '->')? functionname LPAR arguments? RPAR NEWLINE;
	funccall_expr: (expression '->')? functionname LPAR arguments? RPAR;
	nav_expr: self? | (self DOT)? dotexpression;
	self: SELF;

	dotexpression: dotted_name;

	functionname: name;
	arguments: argument (COMMA argument)*;
	argument: (argumentname ASSIGN)? expression;
	argumentname: name;

	assignment: expression ASSIGN expression NEWLINE;
	plusassign: expression PLUSASSIGN expression NEWLINE;
	minusassign: expression MINUSASSIGN expression NEWLINE;

	expression: nav_expr | atomvalue | tuple | vector | dict |
		unopexpr | binopexpr | funccall_expr | selection;
	atomvalue: integervalue | floatvalue | booleanvalue | stringvalue;
	integervalue: integer;
	floatvalue: float;
	booleanvalue: boolean;
	stringvalue: string;

	@unopexpr: parexpr | notexpr | minusexpr;
	parexpr: LPAR expression RPAR;
	notexpr: NOT expression;
	minusexpr: MINUS expression;

	@binopexpr: selection | andexpr | orexpr | lthanexpr | leqthanexpr |
				gthanexpr | geqthanexpr | equalsexpr | nequalsexpr |
				multexpr | divexpr | modexpr | subtractionexpr | sumexpr;

	dict: LSQBR NEWLINE? dictitems NEWLINE? RSQBR;
	dictitems: dictitem (COMMA NEWLINE? dictitem)*;
	dictitem: expression COLON expression;

	vector: LSQBR NEWLINE? (vectoritems NEWLINE?)? RSQBR;
	vectoritems: vectoritem (COMMA NEWLINE? vectoritem)*;
	vectoritem: expression;

	tuple: LPAR tuplearg (COMMA tuplearg)+ RPAR;
	tuplearg: expression;
	selection: expression LSQBR expression RSQBR;
	andexpr: expression LAND expression;
	orexpr: expression LOR expression;
	lthanexpr: expression LTHAN expression;
	leqthanexpr: expression LEQTHAN expression;
	gthanexpr: expression GTHAN expression;
	geqthanexpr: expression GEQTHAN expression;
	equalsexpr: expression EQUALS expression;
	nequalsexpr: expression NEQUALS expression;
	subtractionexpr: expression MINUS expression;
	sumexpr: expression PLUS expression;
	multexpr: expression MULT expression;
	divexpr: expression DIV expression;
	modexpr: expression MOD expression;

	dotted_name: name (DOT name)*;
	name: NAME;
	NAME: '[a-zA-Z_][a-zA-Z_0-9]*(?!r?"|r?\')'
		(%unless
			IMPORT: 'import';
			AS: 'as';
			FROM: 'from';
			NOT: 'not';
			TRUE: 'True';
			FALSE: 'False';
			LAND: 'and';
			LOR: 'or';
            IF: 'if';
            ELSE: 'else';
            WHILE: 'while';
            BREAK: 'break';
            CONTINUE: 'continue';
            RETURN: 'return';
            END: 'end';
            SELF: 'self';
		);

	boolean: TRUE | FALSE;

	DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';
	FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';
	integer: DEC_NUMBER;
	float: FLOAT_NUMBER;

	STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
	LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
	    (%newline)
	    ;
	string: (STRVALUE|LONG_STRVALUE) string?;

	MULT: '\*';
	DIV: '/';
	POTENCY: '@\d';
	LTHAN: '<';
	LEQTHAN: '<=';
	GTHAN: '>';
	GEQTHAN: '>=';
	ASSIGN: '=';
	PLUSASSIGN: '\+=';
	MINUSASSIGN: '\-=';

	DOT: '\.';
	COLON: ':';
	LPAR: '\(';
	RPAR: '\)';
	COMMA: ',';
	EQUALS: '==';
	NEQUALS: '!=';
	PLUS: '\+';
	MINUS: '-';
	MOD: '%';
	LSQBR: '\[';
	RSQBR: '\]';

	LBR: '\{';
	RBR: '\}';

	NEWLINE: '(\r?\n[\t ]*)+'
		(%newline)
		;

	WS: '[\t \f]+' (%ignore);
	COMMENT: '\#[^\n]*'(%ignore);
	
	INDENT: '<INDENT>';
	DEDENT: '<DEDENT>';
};

// specific tokens

CLASS: 'Class';
TOP: 'Top';
BOTTOM: 'Bottom';
INPORT: 'Inport';
OUTPORT: 'Outport';

NAMEATTR: 'name';
DEFAULTATTR: 'default';
TYPEATTR: 'type';
CLASSATTR: 'class';
PRIORITYATTR: 'priority';

ASSOCIATION: 'Association';
INHERITANCE: 'Inheritance';
COMPOSITION: 'Composition';
AGGREGATION: 'Aggregation';
ATTRIBUTE: 'Attribute';

MIN: 'min';
MAX: 'max';

DESTRUCTOR: 'Destructor';
STATEMACHINE: 'StateMachine';
STATE: 'State';
INITIAL: 'initial';
FINAL: 'final';
HISTORY: 'history';
ORTHOGONAL: 'Orthogonal';
TRANSITION: 'Transition';
TARGETATTR: 'target';
PORTATTR: 'port';
ACTIONS: 'Actions';
ONENTER: 'OnEnter';
ONEXIT: 'OnExit';

// general tokens

TRUE: 'True';
FALSE: 'False';

boolean: TRUE | FALSE;

DEC_NUMBER: '[+-]?(0|[1-9]\d*[lL]?)';

FLOAT_NUMBER: '[+-]?((\d+\.\d*|\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+)';

integer: DEC_NUMBER;
float: FLOAT_NUMBER;

STRVALUE : 'u?r?("(?!"").*?(?<!\\)(\\\\)*?"|\'(?!\'\').*?(?<!\\)(\\\\)*?\')' ;
LONG_STRVALUE : '(?s)u?r?(""".*?(?<!\\)(\\\\)*?"""|\'\'\'.*?(?<!\\)(\\\\)*?\'\'\')'
    (%newline)
    ;

string: (STRVALUE|LONG_STRVALUE) string?;

MULT: '\*';
DIV: '/';
POTENCY: '@\d';
LTHAN: '<';
LEQTHAN: '<=';
GTHAN: '>';
GEQTHAN: '>=';
ASSIGN: '=';

DOT: '\.';
COLON: ':';
LPAR: '\(';
RPAR: '\)';
COMMA: ',';
EQUALS: '==';
PLUS: '\+';
MINUS: '-';
MOD: '%';
LSQBR: '\[';
RSQBR: '\]';

NEWLINE: '(\r?\n[\t ]*)+'    // Don't count on the + to prevent multiple NEWLINE tokens. It's just an optimization
    (%newline)
    ;

// ignores
WS: '[\t \f]+' (%ignore);
LINE_CONT: '\\[\t \f]*\r?\n' (%ignore) (%newline);
COMMENT: '\#[^\n]*'(%ignore);

// identation
INDENT: '<INDENT>';
DEDENT: '<DEDENT>';
EOF: '<EOF>';

###
from plyplus.grammars.python_indent_postlex import PythonIndentTracker
self.lexer_postproc = PythonIndentTracker
