
class XML2PythonRules(object):
	def __init__(self):
		self.rules = {
			'SCCD': {
				'type': 'Model',
				'name': 'SCCD',
				'package': 'protected.formalisms',
				'pattern': ['<?xml version="1.0" ?>', '@newline',
							'<diagram name=\"','@SCCD.name','\"','@SCCDauthor', '>',
							'@newline',
							'@indent',
								'@SCCDdescription',
								'@SCCDInPort',
								'@SCCDOutPort',
								'@SCCDTop',
								'@SCCDClass',
								'@SCCDBottom',
							'@dedent', '</diagram>'
					]
			},
			'SCCDauthor': {
				'type': 'Attribute',
				'pattern': [' author=\"','@SCCD.author','\"']
			},
			'SCCDdescription': {
				'type': 'Attribute',
				'pattern': ['<description>', '@newline', '@indent',
							'@SCCD.description','@newline', '@dedent',
							'</description>', '@newline']
			},
			'SCCDInPort': {
				'type': 'Class',
				'name': 'SCCD.InPort',
				'pattern': ['<inport name="', '@Named.name','"/>', '@newline']
			},
			'SCCDOutPort': {
				'type': 'Class',
				'name': 'SCCD.OutPort',
				'pattern': ['<outport name="', '@Named.name','"/>', '@newline']
			},
			'SCCDTop': {
				'type': 'Class',
				'name': 'SCCD.Top',
				'pattern': ['<top>', '@newline', '@indent', '@@',
								'from sccd.runtime.libs.ui import *', '@newline',
								'from sccd.runtime.libs.utils import *', '@newline',
								'@ActionBlockStatement',
				'@dedent', '</top>', '@newline' ]
			},
			'SCCDBottom': {
				'type': 'Class',
				'name': 'SCCD.Bottom',
				'pattern': ['<bottom>', '@newline', '@indent',
								'@ActionBlockStatement',
				'@dedent', '</bottom>', '@newline' ]
			},
			'SCCDActionBlock': {
				'type': 'Class',
				'name': 'SCCD.ActionBlock',
				'pattern': ['@indent','@ActionBlockStatement', '@dedent']
			},
			'ActionBlockStatement': {
				'type': 'Association',
				'name': 'SCCD.actionblock_statement',
				'target': 'SCCD.Statement',
				'pattern': ['@SCCDStatement']
			},
			'SCCDStatement': {
				'type': 'Class',
				'name': 'SCCD.Statement',
				'pattern': [
								'@StatementMethodCall',
								'@StatementImport',
								'@StatementAssignment',
								'@StatementWhile',
								'@StatementIfElse',
								'@StatementReturn',
								'@StatementContinue',
								'@StatementBreak',
								'@StatementDeclaration',
								'@NextStatement'
							]
			},
			'NextStatement': {
				'type': 'Association',
				'name': 'SCCD.statement_statement_next',
				'target': 'SCCD.Statement',
				'pattern': [
							'@SCCDStatement'
							]
			},
			'StatementDeclaration': {
				'type': 'Class',
				'name': 'SCCD.Declaration',
				'pattern': [ #'@DeclarationType', not used in python nor javascript
								'@Declaration.name',
								'@DeclarationInit', '@newline'
					]
			},
			'DeclarationType': {
				'type': 'Association',
				'name': 'SCCD.declaration_navigationexpression_type',
				'target': 'SCCD.NavigationExpression',
				'pattern': [ '@SCCDNavExpr', ' ' ]
			},
			'DeclarationInit': {
				'type': 'Association',
				'name': 'SCCD.declaration_expression_init',
				'target': 'SCCD.Expression',
				'pattern': [ ' = ','@SCCDExpression' ]
			},
			'StatementReturn': {
				'type': 'Class',
				'name': 'SCCD.Return',
				'pattern': [ 'return', '@ReturnExpression', '@newline'
					]
			},
			'ReturnExpression': {
				'type': 'Association',
				'name': 'SCCD.return_expression',
				'target': 'SCCD.Expression',
				'pattern': [ ' ','@SCCDExpression' ]
			},
			'StatementContinue': {
				'type': 'Class',
				'name': 'SCCD.Continue',
				'pattern': [ 'continue', '@newline' ]
			},
			'StatementBreak': {
				'type': 'Class',
				'name': 'SCCD.Break',
				'pattern': [ 'break', '@newline' ]
			},
			'StatementWhile': {
				'type': 'Class',
				'name': 'SCCD.While',
				'pattern': [ 'while ', '@WhileCondition', ':', '@newline',
							'@WhileBody'
					]
			},
			'WhileCondition': {
				'type': 'Association',
				'name': 'SCCD.while_expression_condition',
				'target': 'SCCD.Expression',
				'pattern': [
							'@SCCDExpression'
							]
			},
			'WhileBody': {
				'type': 'Association',
				'name': 'SCCD.while_actionblock_body',
				'target': 'SCCD.ActionBlock',
				'pattern': ['@newline','@SCCDActionBlock','@newline']
			},
			'StatementIfElse': {
				'type': 'Class',
				'name': 'SCCD.IfElse',
				'pattern': [ 'if ', '@IfElseCondition', ':',
							'@IfBody','@ElseBody'
					]
			},
			'IfElseCondition': {
				'type': 'Association',
				'name': 'SCCD.ifelse_expression_condition',
				'target': 'SCCD.Expression',
				'pattern': [
							'@SCCDExpression'
							]
			},
			'IfBody': {
				'type': 'Association',
				'name': 'SCCD.ifelse_actionblock_ifbody',
				'target': 'SCCD.ActionBlock',
				'pattern': ['@newline','@SCCDActionBlock']
			},
			'ElseBody': {
				'type': 'Association',
				'name': 'SCCD.ifelse_actionblock_elsebody',
				'target': 'SCCD.ActionBlock',
				'pattern': [
							'else:',
							'@newline',
							'@SCCDActionBlock'
							]
			},
			'StatementAssignment': {
				'type': 'Class',
				'name': 'SCCD.Assignment',
				'pattern': [
								'@AssignmentLeft',
								'@StatementPlainAssignment',
								'@StatementPlusAssignment',
								'@StatementMinusAssignment',
								'@AssignmentRight','@newline'
							]
			},
			'StatementPlainAssignment': {
				'type': 'Class',
				'name': 'SCCD.PlainAssignment',
				'pattern': [ ' = ' ]
			},
			'StatementPlusAssignment': {
				'type': 'Class',
				'name': 'SCCD.PlusAssignment',
				'pattern': [ ' += ' ]
			},
			'StatementMinusAssignment': {
				'type': 'Class',
				'name': 'SCCD.MinusAssignment',
				'pattern': [ ' -= ' ]
			},
			'AssignmentLeft': {
				'type': 'Association',
				'name': 'SCCD.assignment_expression_left',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'AssignmentRight': {
				'type': 'Association',
				'name': 'SCCD.assignment_expression_right',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'StatementMethodCall': {
				'type': 'Class',
				'name': 'SCCD.MethodCallStm',
				'pattern': [
								'@Sender',
								'@AbsMethodCall.name','(',
								'@Arguments',
								')','@newline'
							]
			},
			'Sender': {
				'type': 'Association',
				'name': 'SCCD.methodcall_sender',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression', '.' ]
			},
			'SCCDNavExpr': {
				'type': 'Class',
				'name': 'SCCD.NavigationExpression',
				'pattern': [ '@FirstNavigation' ]
			},
			'FirstNavigation': {
				'type': 'Association',
				'name': 'SCCD.navigationexpression_absnavigationexpression',
				'target': 'SCCD.AbsNavigationExpression',
				'pattern': [ '@SCCDDotExpr', '@SCCDSelfExpr' ]
			},
			'SCCDDotExpr': {
				'type': 'Class',
				'name': 'SCCD.DotExpression',
				'pattern': [ '@DotExpression.path' ]
			},
			'SCCDSelfExpr': {
				'type': 'Class',
				'name': 'SCCD.SelfExpression',
				'pattern': [ 'self','@@','@NextDot' ]
			},
			'NextDot': {
				'type': 'Association',
				'name': 'SCCD.selfexpression_dotexpression',
				'target': 'SCCD.DotExpression',
				'pattern': [ '.','@SCCDDotExpr' ]
			},
			'SCCDMethodCall': {
				'type': 'Class',
				'name': 'SCCD.MethodCall',
				'pattern': [
								'@Sender',
								'@AbsMethodCall.name','(',
								'@Arguments',
								')'
							]
			},
			'SCCDUnop': {
				'type': 'Class',
				'name': 'SCCD.Unop',
				'pattern': [
								'@SCCDNot',
								'@SCCDMinus',
								'@SCCDParenthesis'
				]
			},
			'SCCDNot': {
				'type': 'Class',
				'name': 'SCCD.Not',
				'pattern': [ 'not ', '@UnopExpression' ]
			},
			'SCCDMinus': {
				'type': 'Class',
				'name': 'SCCD.Minus',
				'pattern': [ '-', '@UnopExpression' ]
			},
			'SCCDParenthesis': {
				'type': 'Class',
				'name': 'SCCD.Parenthesis',
				'pattern': [ '(', '@UnopExpression', ')' ]
			},
			'UnopExpression': {
				'type': 'Association',
				'name': 'SCCD.unop_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'SCCDBinop': {
				'type': 'Class',
				'name': 'SCCD.Binop',
				'pattern': [
								'@SCCDAnd',
								'@SCCDOr',
								'@SCCDNEqual',
								'@SCCDEqual',
								'@SCCDLEThan',
								'@SCCDLThan',
								'@SCCDGEThan',
								'@SCCDGThan',
								'@SCCDMod',
								'@SCCDDiv',
								'@SCCDMult',
								'@SCCDAdd',
								'@SCCDSubtract',
								'@SCCDSelection'
				]
			},
			'BinopLeft': {
				'type': 'Association',
				'name': 'SCCD.binop_expression_left',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'BinopRight': {
				'type': 'Association',
				'name': 'SCCD.binop_expression_right',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'SCCDAnd': {
				'type': 'Class',
				'name': 'SCCD.And',
				'pattern': [
								'@BinopLeft',
								' and ',
								'@BinopRight'
							]
			},
			'SCCDOr': {
				'type': 'Class',
				'name': 'SCCD.Or',
				'pattern': [
								'@BinopLeft',
								' or ',
								'@BinopRight'
							]
			},
			'SCCDNEqual': {
				'type': 'Class',
				'name': 'SCCD.NEqual',
				'pattern': [
								'@BinopLeft',
								' != ',
								'@BinopRight'
							]
			},
			'SCCDEqual': {
				'type': 'Class',
				'name': 'SCCD.Equal',
				'pattern': [
								'@BinopLeft',
								' == ',
								'@BinopRight'
							]
			},
			'SCCDLEThan': {
				'type': 'Class',
				'name': 'SCCD.LEThan',
				'pattern': [
								'@BinopLeft',
								' <= ',
								'@BinopRight'
							]
			},
			'SCCDLThan': {
				'type': 'Class',
				'name': 'SCCD.LThan',
				'pattern': [
								'@BinopLeft',
								' < ',
								'@BinopRight'
							]
			},
			'SCCDGEThan': {
				'type': 'Class',
				'name': 'SCCD.GEThan',
				'pattern': [
								'@BinopLeft',
								' >= ',
								'@BinopRight'
							]
			},
			'SCCDGThan': {
				'type': 'Class',
				'name': 'SCCD.GThan',
				'pattern': [
								'@BinopLeft',
								' > ',
								'@BinopRight'
							]
			},
			'SCCDMod': {
				'type': 'Class',
				'name': 'SCCD.Mod',
				'pattern': [
								'@BinopLeft',
								' % ',
								'@BinopRight'
							]
			},
			'SCCDDiv': {
				'type': 'Class',
				'name': 'SCCD.Div',
				'pattern': [
								'@BinopLeft',
								' / ',
								'@BinopRight'
							]
			},
			'SCCDMult': {
				'type': 'Class',
				'name': 'SCCD.Mult',
				'pattern': [
								'@BinopLeft',
								' * ',
								'@BinopRight'
							]
			},
			'SCCDAdd': {
				'type': 'Class',
				'name': 'SCCD.Add',
				'pattern': [
								'@BinopLeft',
								' + ',
								'@BinopRight'
							]
			},
			'SCCDSubtract': {
				'type': 'Class',
				'name': 'SCCD.Subtract',
				'pattern': [
								'@BinopLeft',
								' - ',
								'@BinopRight'
							]
			},
			'SCCDSelection': {
				'type': 'Class',
				'name': 'SCCD.Selection',
				'pattern': [
								'@BinopLeft',
								'[',
									'@BinopRight',
								']'
							]
			},
			'SCCDComposite': {
				'type': 'Class',
				'name': 'SCCD.Composite',
				'pattern': [ '@SCCDTuple', '@SCCDDict', '@SCCDArray' ]
			},
			'SCCDTuple': {
				'type': 'Class',
				'name': 'SCCD.Tuple',
				'pattern': [
								'(', '@CompositeArguments', ')'
				]
			},
			'SCCDArray': {
				'type': 'Class',
				'name': 'SCCD.Array',
				'pattern': [
								'[', '@CompositeArguments', ']'
				]
			},
			'SCCDDict': {
				'type': 'Class',
				'name': 'SCCD.Dict',
				'pattern': [
								'{', '@CompositeArguments', '}'
				]
			},
			'SCCDAtomValue': {
				'type': 'Class',
				'name': 'SCCD.AtomValue',
				'pattern': [
								'@SCCDStringValue',
								'@SCCDIntegerValue',
								'@SCCDBooleanValue',
								'@SCCDFloatValue'
				]
			},
			'SCCDStringValue': {
				'type': 'Class',
				'name': 'SCCD.StringValue',
				'pattern': [
								'\'',
								'@StringValue.value',
								'\''
				]
			},
			'SCCDIntegerValue': {
				'type': 'Class',
				'name': 'SCCD.IntegerValue',
				'pattern': [
								'@IntegerValue.value',
				]
			},
			'SCCDFloatValue': {
				'type': 'Class',
				'name': 'SCCD.FloatValue',
				'pattern': [
								'@FloatValue.value',
				]
			},
			'SCCDBooleanValue': {
				'type': 'Class',
				'name': 'SCCD.BooleanValue',
				'pattern': [
								'@BooleanValue.value',
				]
			},
			'CompositeArguments': {
				'type': 'Association',
				'name': 'SCCD.composite_compositeargument',
				'target': 'SCCD.CompositeArgument',
				'pattern': [ '@CompositeArgument' ]
			},
			'CompositeArgument': {
				'type': 'Class',
				'name': 'SCCD.CompositeArgument',
				'pattern': [
								'@RegularArgument',
								'@DictArgument'
				]
			},
			'RegularArgument': {
				'type': 'Class',
				'name': 'SCCD.RegularArgument',
				'pattern': [
								'@RegularArgumentValue',
								'@CompositeArgumentNext'
				]
			},
			'RegularArgumentValue': {
				'type': 'Association',
				'name': 'SCCD.regularargument_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'DictArgument': {
				'type': 'Class',
				'name': 'SCCD.DictArgument',
				'pattern': [
								'@DictArgumentLabel',':',
								'@DictArgumentValue',
								'@CompositeArgumentNext'
				]
			},
			'DictArgumentLabel': {
				'type': 'Association',
				'name': 'SCCD.dictargument_labelexpression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'DictArgumentValue': {
				'type': 'Association',
				'name': 'SCCD.dictargument_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'CompositeArgumentNext': {
				'type': 'Association',
				'name': 'SCCD.compositeargument_compositeargument_next',
				'target': 'SCCD.CompositeArgument',
				'pattern': [ ', ', '@CompositeArgument' ]
			},
			'Arguments': {
				'type': 'Association',
				'name': 'SCCD.methodcall_argument',
				'target': 'SCCD.Argument',
				'pattern': [ '@SCCDArgument' ]
			},
			'SCCDArgument': {
				'type': 'Class',
				'name': 'SCCD.Argument',
				'pattern': [
								'@ArgumentName',
								'@ArgumentValue',
								'@ArgumentNext'
				]
			},
			'ArgumentName': {
				'type': 'Attribute',
				'pattern': [ '@Argument.name', '=']
			},
			'ArgumentValue': {
				'type': 'Association',
				'name': 'SCCD.argument_value',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'ArgumentNext': {
				'type': 'Association',
				'name': 'SCCD.argument_argument_next',
				'target': 'SCCD.Argument',
				'pattern': [ ', ', '@SCCDArgument' ]
			},
			'SCCDExpression': {
				'type': 'Class',
				'name': 'SCCD.Expression',
				'pattern': [
								'@SCCDNavExpr',
								'@SCCDAtomValue',
								'@SCCDUnop',
								'@SCCDBinop',
								'@SCCDMethodCall',
								'@SCCDComposite'
							]
			},
			'StatementImport': {
				'type': 'Class',
				'name': 'SCCD.Import',
				'pattern': [
								'@ImportFrom',
								'import ', '@Import.location',
								'@ImportAs','@newline'
							]
			},
			'ImportFrom': {
				'type': 'Attribute',
				'pattern': ['from ', '@Import.from' ,' ']
			},
			'ImportAs': {
				'type': 'Attribute',
				'pattern': [' as ', '@Import.as']
			},
			'SCCDClass': {
				'type': 'Class',
				'name': 'SCCD.Class',
				'pattern': ['<class name="', '@Named.name', '"',
								'@ClassDefault', '>',
								'@newline','@indent',
								'@ClassInports',
								'@ClassRelationships',
								'@ClassAttributes',
								'@ClassMethods',
								'@ClassStateMachine',
								'@dedent',
								'</class>','@newline'
							]
			},
			'ClassDefault': {
				'type': 'Attribute',
				'pattern': [' default="', '@Class.default' ,'"']
			},
			'ClassStateMachine': {
				'type': 'Association',
				'name': 'SCCD.class_statemachine',
				'target': 'SCCD.StateMachine',
				'pattern': [
							'<scxml ', '@StateMachinePseudoStates','>', '@newline',
							'@indent',
							'@StateMachineStates',
							'@HistoryOnStateMachine',
							'@TransitionsOnStateMachine',
							'@dedent',
							'</scxml>', '@newline'
							]
			},
			'StateMachineStates': {
				'type': 'Association',
				'name': 'SCCD.statemachine_absstate',
				'target': 'SCCD.AbsState',
				'pattern': [
								'@SCCDState',
								'@SCCDOrthogonalComponent'
				]
			},
			'SCCDState': {
				'type': 'Class',
				'name': 'SCCD.State',
				'pattern': [
					'<state id="', '@AbsState.name', '"', '@StatePseudoStates','>',
					'@newline',
					'@indent',
					'@OnEnter',
					'@OnExit',
					'@Transitions',
					'@HistoryOnPseudoStates',
					'@InnerStates',
					'@dedent',
					'</state>','@newline'
				]
			},
			'SCCDOrthogonalComponent': {
				'type': 'Class',
				'name': 'SCCD.OrthogonalComponent',
				'pattern': [
					'<parallel id="', '@AbsState.name', '"', '@StatePseudoStates','>',
					'@newline',
					'@indent',
					'@OnEnter',
					'@OnExit',
					'@Transitions',
					'@HistoryOnPseudoStates',
					'@InnerStates',
					'@dedent',
					'</parallel>','@newline'
				]
			},
			'OnEnter': {
				'type': 'Association',
				'name': 'SCCD.absstate_onenter',
				'target': 'SCCD.ActionBlock',
				'pattern': [
								'<onentry>','@newline',
								'@indent',
								'<script>', '@newline',
								'<![CDATA[','@newline',
								'@SCCDActionBlock',
								']]>',
								'@newline','</script>', '@newline',
							'@dedent','</onentry>', '@newline'
							]
			},
			'OnExit': {
				'type': 'Association',
				'name': 'SCCD.absstate_onexit',
				'target': 'SCCD.ActionBlock',
				'pattern': [
								'<onexit>','@newline',
								'@indent',
								'<script>', '@newline',
								'<![CDATA[','@newline',
								'@SCCDActionBlock',
								']]>',
								'@newline','</script>', '@newline',
							'@dedent','</onexit>', '@newline'
							]
			},
			'TransitionsOnStateMachine': {
				'type': 'Association',
				'name': 'SCCD.statemachine_transition',
				'target': 'SCCD.Transition',
				'pattern': [
								'@SCCDTransition'
				]
			},
			'Transitions': {
				'type': 'Association',
				'name': 'SCCD.absstate_transition',
				'target': 'SCCD.Transition',
				'pattern': [
								'@SCCDTransition'
				]
			},
			'SCCDTransition': {
				'type': 'Class',
				'name': 'SCCD.Transition',
				'pattern': [
								'<transition',
								'@TransitionAfter',
								'@TransitionPort',
								'@TransitionTarget',
								'@TransitionEventName',
								'@TransitionCondition',
								'>','@newline',
								'@EventParameters',
								'@RaiseEvents',
								'@TransitionActionBlock',
								'</transition>','@newline'
				]
			},
			'TransitionActionBlock': {
				'type': 'Association',
				'name': 'SCCD.transition_actionblock',
				'target': 'SCCD.ActionBlock',
				'pattern': ['@indent',
								'<script>', '@newline', '@indent',
								'<![CDATA[','@newline',
								'@SCCDActionBlock',
								']]>',
								'@newline','@dedent','</script>',
							'@dedent', '@newline'
							]
			},
			'RaiseEvents': {
				'type': 'Association',
				'name': 'SCCD.transition_raise',
				'target': 'SCCD.Raise',
				'pattern': [ '@indent','@SCCDRaise','@dedent' ]
			},
			'SCCDRaise': {
				'type': 'Class',
				'name': 'SCCD.Raise',
				'pattern': [
							'<raise ',
							'@RaiseEventName',
							'@RaiseScope',
							'@RaiseTarget',
							'>', '@newline',
							'@RaiseEventParameters',
							'</raise>', '@newline',
				]
			},
			'RaiseEventParameters': {
				'type': 'Association',
				'name': 'SCCD.raise_methodcall',
				'target': 'SCCD.MethodCall',
				'pattern': [ '@SCCDMethodArgs' ]
			},
			'SCCDMethodArgs': {
				'type': 'Class',
				'name': 'SCCD.MethodCall',
				'pattern': ['@MethodArguments']
			},
			'MethodArguments': {
				'type': 'Association',
				'name': 'SCCD.methodcall_argument',
				'target': 'SCCD.Argument',
				'pattern': [ '@SCCDRaiseArgument' ]
			},
			'SCCDRaiseArgument': {
				'type': 'Class',
				'name': 'SCCD.Argument',
				'pattern': [
								'@indent',
								'<parameter expr="',
								'@ArgumentValue', '"/>',
								'@dedent','@newline',
								'@RaiseArgumentNext',
				]
			},
			'RaiseArgumentNext': {
				'type': 'Association',
				'name': 'SCCD.argument_argument_next',
				'target': 'SCCD.Argument',
				'pattern': [ '@SCCDRaiseArgument' ]
			},
			'RaiseEventName': {
				'type': 'Association',
				'name': 'SCCD.raise_methodcall',
				'target': 'SCCD.MethodCall',
				'pattern': [ '@SCCDMethodName' ]
			},
			'SCCDMethodName': {
				'type': 'Class',
				'name': 'SCCD.MethodCall',
				'pattern': [
							'event="','@AbsMethodCall.name','"'
				]
			},
			'RaiseScope': {
				'type': 'Association',
				'name': 'SCCD.raise_scope',
				'target': 'SCCD.Scope',
				'pattern': [ '@SCCDScope' ]
			},
			'SCCDScope': {
				'type': 'Class',
				'name': 'SCCD.Scope',
				'pattern': [
							' scope="','@ScopeExpression','"'
				]
			},
			'ScopeExpression': {
				'type': 'Association',
				'name': 'SCCD.scope_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'RaiseTarget': {
				'type': 'Association',
				'name': 'SCCD.raise_target',
				'target': 'SCCD.Target',
				'pattern': [ '@SCCDTarget' ]
			},
			'SCCDTarget': {
				'type': 'Class',
				'name': 'SCCD.Target',
				'pattern': [
							' target="','@TargetExpression','"'
				]
			},
			'TargetExpression': {
				'type': 'Association',
				'name': 'SCCD.target_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'TransitionCondition': {
				'type': 'Association',
				'name': 'SCCD.transition_guard',
				'target': 'SCCD.Guard',
				'pattern': [ '@SCCDGuard' ]
			},
			'SCCDGuard': {
				'type': 'Class',
				'name': 'SCCD.Guard',
				'pattern': [' cond="', '@GuardExpression', '"']
			},
			'GuardExpression': {
				'type': 'Association',
				'name': 'SCCD.guard_expression',
				'target': 'SCCD.Expression',
				'pattern': [ '@SCCDExpression' ]
			},
			'TransitionAfter': {
				'type': 'Association',
				'name': 'SCCD.after_expression',
				'target': 'SCCD.Expression',
				'pattern': [' after="', '@SCCDExpression' ,'"']
			},
			'TransitionTarget': {
				'type': 'Attribute',
				'pattern': [' target="', '@Transition.target' ,'"']
			},
			'EventParameters': {
				'type': 'Association',
				'name': 'SCCD.transition_event_trigger',
				'target': 'SCCD.Event',
				'pattern': [ '@SCCDTransitionEventParams' ]
			},
			'SCCDTransitionEventParams': {
				'type': 'Class',
				'name': 'SCCD.Event',
				'pattern': ['@FirstEventParameter']
			},
			'FirstEventParameter': {
				'type': 'Association',
				'name': 'SCCD.event_parameter',
				'target': 'SCCD.Parameter',
				'pattern': [
								'@indent',
								'<parameter ',
								'@SCCDParameter', '/>',
								'@dedent','@newline',
								'@ParameterNext'
							]
			},
			'TransitionEventName': {
				'type': 'Association',
				'name': 'SCCD.transition_event_trigger',
				'target': 'SCCD.Event',
				'pattern': [ '@SCCDTransitionEventName' ]
			},
			'SCCDTransitionEventName': {
				'type': 'Class',
				'name': 'SCCD.Event',
				'pattern': [' event="', '@Event.name' ,'"']
			},
			'TransitionPort': {
				'type': 'Association',
				'name': 'SCCD.transition_inport',
				'target': 'SCCD.InPort',
				'pattern': [
								'@SCCDTransitionInPort'
				]
			},
			'SCCDTransitionInPort': {
				'type': 'Class',
				'name': 'SCCD.InPort',
				'pattern': [' port="', '@Named.name' ,'"']
			},

			'InnerStates': {
				'type': 'Association',
				'name': 'SCCD.absstate_absstate_inner',
				'target': 'SCCD.AbsState',
				'pattern': [
								'@SCCDState',
								'@SCCDOrthogonalComponent'
				]
			},
			'StatePseudoStates': {
				'type': 'Association',
				'name': 'SCCD.absstate_pseudostate',
				'target': 'SCCD.PseudoState',
				'pattern': [
								'@SCCDInitialState',
								'@SCCDFinalState'
				]
			},
			'HistoryOnPseudoStates': {
				'type': 'Association',
				'name': 'SCCD.absstate_pseudostate',
				'target': 'SCCD.PseudoState',
				'pattern': [
								'@SCCDHistoryState'
				]
			},
			'HistoryOnStateMachine': {
				'type': 'Association',
				'name': 'SCCD.statemachine_pseudostate',
				'target': 'SCCD.PseudoState',
				'pattern': [
								'@SCCDHistoryState'
				]
			},
			'StateMachinePseudoStates': {
				'type': 'Association',
				'name': 'SCCD.statemachine_pseudostate',
				'target': 'SCCD.PseudoState',
				'pattern': [
								'@SCCDInitialState',
								'@SCCDFinalState'
				]
			},
			'SCCDInitialState': {
				'type': 'Class',
				'name': 'SCCD.InitialState',
				'pattern': [' initial="', '@PseudoState.name', '"' ]
			},
			'SCCDFinalState': {
				'type': 'Class',
				'name': 'SCCD.FinalState',
				'pattern': [' final="', '@PseudoState.name', '"' ]
			},
			'SCCDHistoryState': {
				'type': 'Class',
				'name': 'SCCD.HistoryState',
				'pattern': ['<history id="', '@PseudoState.name', '"/>', '@newline' ]
			},
			'ClassInports': {
				'type': 'Association',
				'name': 'SCCD.class_inport',
				'target': 'SCCD.InPort',
				'pattern': ['@SCCDInPort']
			},
			'ClassRelationships': {
				'type': 'Association',
				'name': 'SCCD.class_relationship',
				'target': 'SCCD.Relationship',
				'pattern': [
							'<relationships>', '@newline',
							'@indent',
								'@ClassAssociation',
								'@ClassInheritance',
							'@dedent',
							'</relationships>', '@newline'
							]
			},
			'ClassAssociation': {
				'type': 'Class',
				'name': 'SCCD.Association',
				'pattern': ['<association name="',
								'@Association.name', '"',
								'@RelationshipClass',
								'@RelationshipMin',
								'@RelationshipMax',
								'/>',
								'@newline'
							]
			},
			'ClassInheritance': {
				'type': 'Class',
				'name': 'SCCD.Inheritance',
				'pattern': ['<inheritance',
								'@RelationshipClass',
								' priority="','@Inheritance.priority','"',
								'/>',
								'@newline'
							]
			},
			'RelationshipClass': {
				'type': 'Attribute',
				'pattern': [' class="','@Relationship.class', '"']
			},
			'RelationshipMin': {
				'type': 'Attribute',
				'pattern': [' min="','@Relationship.min', '"']
			},
			'RelationshipMax': {
				'type': 'Attribute',
				'pattern': [' max="','@Relationship.max', '"']
			},
			'ClassAttributes': {
				'type': 'Association',
				'name': 'SCCD.class_attribute',
				'target': 'SCCD.Attribute',
				'pattern': [ '@ClassAttribute' ]
			},
			'ClassAttribute': {
				'type': 'Class',
				'name': 'SCCD.Attribute',
				'pattern': [
								'<attribute name="', '@Named.name', '"',
								'@AttributeType', '@AttributeDefault',
								'/>',
								'@newline'
							]
			},
			'AttributeType': {
				'type': 'Attribute',
				'pattern': [' type="','@Attribute.type', '"']
			},
			'AttributeDefault': {
				'type': 'Attribute',
				'pattern': [' type="','@Attribute.default', '"']
			},
			'ClassMethods': {
				'type': 'Association',
				'name': 'SCCD.class_method',
				'target': 'SCCD.AbsMethod',
				'pattern': [
							'@ClassConstructor',
							'@ClassDestructor',
							'@ClassMethod'
				]
			},
			'ClassConstructor': {
				'type': 'Class',
				'name': 'SCCD.Constructor',
				'pattern': [
								'<method name="', '@-(SCCD.class_method).Named.name', '"', '>',
								'@newline',
								'@AbsMethodParameters',
								'@AbsMethodBody',
								'</method>', '@newline'
							]
			},
			'ClassDestructor': {
				'type': 'Class',
				'name': 'SCCD.Destructor',
				'pattern': [
								'<method name="~', '@-(SCCD.class_method).Named.name', '"', '>',
								'@newline',
								'@AbsMethodBody',
								'</method>', '@newline'
							]
			},
			'ClassMethod': {
				'type': 'Class',
				'name': 'SCCD.Method',
				'pattern': [
								'<method name="', '@Method.name', '"', '>',
								'@newline',
								'@AbsMethodParameters',
								'@AbsMethodBody',
								'</method>', '@newline'
							]
			},
			'AbsMethodParameters': {
				'type': 'Association',
				'name': 'SCCD.absmethod_parameter',
				'target': 'SCCD.Parameter',
				'pattern': [
								'@indent',
								'<parameter ',
								'@SCCDParameter', '/>',
								'@dedent', '@newline',
								'@ParameterNext'
							]
			},
			'ParameterNext': {
				'type': 'Association',
				'name': 'SCCD.parameter_parameter_next',
				'target': 'SCCD.Parameter',
				'pattern': [
								'@indent',
								'<parameter ',
								'@SCCDParameter', '/>',
								'@dedent', '@newline',
								'@ParameterNext'
							]
			},
			'SCCDParameter': {
				'type': 'Class',
				'name': 'SCCD.Parameter',
				'pattern': [
								'name="','@Parameter.name','"',
								'@ParameterType',
								'@ParameterDefault'
							]
			},
			'ParameterType': {
				'type': 'Association',
				'name': 'SCCD.parameter_type_expression',
				'target': 'SCCD.NavigationExpression',
				'pattern': [ ' type="','@SCCDNavExpr', '"']
			},
			'ParameterDefault': {
				'type': 'Attribute',
				'pattern': [ ' default="','@Parameter.default','"' ]
			},
			'AbsMethodBody': {
				'type': 'Association',
				'name': 'SCCD.absmethod_actionblock_body',
				'target': 'SCCD.ActionBlock',
				'pattern': ['@indent',
								'<body>', '@newline',
								'<![CDATA[','@newline',
								'@SCCDActionBlock',
								']]>','@newline',
								'</body>',
							'@dedent', '@newline'
							]
			}
		}

