
class SCCD_ASG_Mapper(object):
	def __init__(self):
		self.metamodel_location = 'protected.formalisms.SCCD'
		self.metamodel_path = 'sccd_modelverse_sources/sccd_metamodel.mtn'
		self.rules = {
			'sccd': {'name': 'SCCD',
					 'type': 'Model',
					 'body':
						{
							'name': ('attrname.string','String'),
							'author': ('attrauthor.string','String'),
							'description': ('attrdescription.string','String')
						}
					},
			'class': {
						'name': 'Class',
						'type': 'Class',
						'body':
						{
							'name': ('nameattr.string','String'),
							'default': ('defaultattr.boolean','Boolean')
						}
					},
			'inheritance': { 'name': 'Inheritance',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'inheritance_', ['getNodeId']],
							'priority': ('priorityattr.integer','Integer'),
							'class': ('classattr.string','String')
						}
					},
			'association': { 'name': 'Association',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'association_', ['getNodeId']],
							'name': ('nameattr.string','String'),
							'class': ('classattr.string','String'),
							'min': ('minattr.integer','Integer'),
							'max': ('maxattr.integer','Integer')
						}
					},
			'composition': { 'name': 'Composition',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'composition_', ['getNodeId']],
							'class': ('classattr.string','String'),
							'min': ('minattr.integer','Integer'),
							'max': ('maxattr.integer','Integer')
						}
					},
			'aggregation': { 'name': 'Aggregation',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'aggregation_', ['getNodeId']],
							'class': ('classattr.string','String'),
							'min': ('minattr.integer','Integer'),
							'max': ('maxattr.integer','Integer')
						}
					},
			'attribute': { 'name': 'Attribute',
						'type': 'Class',
						'body':
						{
							'name': ('nameattr.string','String'),
							'type': ('typenameattr.string','String'),
							'default': ('defaultvalueattr.string','String')
						}
					},
			'top': { 	'name': 'Top',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'top_', ['getNodeId']]
						}
					},
			'bottom': { 'name': 'Bottom',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'bottom_', ['getNodeId']]
						}
					},
			'constructor': { 'name': 'Constructor',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'constructor_', ['getNodeId']]
						}
					},
			'destructor': { 'name': 'Destructor',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'destructor_', ['getNodeId']]
						}
					},
			'method': { 'name': 'Method',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'method_', ['getNodeId']],
							'name': ('methodname.name', 'String')
						}
					},
			'body': {
						'name': 'ActionBlock',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'body_', ['getNodeId']]
						}
					},
			'onenter': {
						'name': 'OnEnter',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'onenter_', ['getNodeId']]
						}
					},
			'onexit': {
						'name': 'OnExit',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'onexit_', ['getNodeId']]
						}
					},
			'import': { 	'name': 'Import',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'import_', ['getNodeId']],
								'location': ('importname.dotted_name','String'),
								'from': ('fromname.dotted_name','String'),
								'as': ('asname.name','String')
							}
					},
			'decl_stm': { 	'name': 'Declaration',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'declaration_', ['getNodeId']],
								'name': ('decl_name.name','String')
							}
					},
			'assignment': { 	'name': 'PlainAssignment',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'plainassignment_', ['getNodeId']]
							}
					},
			'plusassign': { 	'name': 'PlusAssignment',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'plusassignment_', ['getNodeId']]
							}
					},
			'minusassign': { 	'name': 'MinusAssignment',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'minusassignment_', ['getNodeId']]
							}
					},
			'funccall_stm': {
							'name': 'MethodCallStm',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'methodcallstm_', ['getNodeId']],
								'name': ('functionname','String')
							}
					},
			'nav_expr': {
							'name': 'NavigationExpression',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'nav_', ['getNodeId']]
							}
					},
			'self': {
							'name': 'SelfExpression',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'selfexpression_', ['getNodeId']]
							}
					},
			'dotexpression': {
							'name': 'DotExpression',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'dotexpression_', ['getNodeId']],
								'path': ('dotexpression.dotted_name','String')
							}
					},
			'funccall_expr': {
							'name': 'MethodCall',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'methodcall_', ['getNodeId']],
								'name': ('functionname','String')
							}
					},
			'stringvalue': {
							'name': 'StringValue',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'string_', ['getNodeId']],
								'value': ('stringvalue.string','String')
							}
					},
			'integervalue': {
							'name': 'IntegerValue',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'integer_', ['getNodeId']],
								'value': ('integervalue.integer','Integer')
							}
					},
			'floatvalue': {
							'name': 'FloatValue',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'float_', ['getNodeId']],
								'value': ('floatvalue.float','Float')
							}
					},
			'booleanvalue': {
							'name': 'BooleanValue',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'boolean_', ['getNodeId']],
								'value': ('booleanvalue.boolean','Boolean')
							}
					},
			'argument': {
							'name': 'Argument',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'argument_', ['getNodeId']],
								'name': ('argumentname','String')
							}
					},
			'formalparameter': {
							'name': 'Parameter',
							'type': 'Class',
							'body':
							{
								'id': ['concat', 'parameter_', ['getNodeId']],
								'name': ('namevalue.name','String'),
								'default': ('defaultvalue.atomvalue','String')
							}
					},
			'statemachine': { 'name': 'StateMachine',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'statemachine_', ['getNodeId']]
						}
					},
			'state': { 'name': 'State',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'state_', ['getNodeId']],
							'name': ('statename.string','String')
						}
					},
			'orthogonal': { 'name': 'OrthogonalComponent',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'orthogonal_', ['getNodeId']],
							'name': ('statename.string','String')
						}
					},
			'initial': { 'name': 'InitialState',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'initial_', ['getNodeId']],
							'name': ('statename.string','String')
						}
					},
			'final': { 'name': 'FinalState',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'final_', ['getNodeId']],
							'name': ('statename.string','String')
						}
					},
			'history': { 'name': 'HistoryState',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'history_', ['getNodeId']],
							'name': ('statename.string','String')
						}
					},
			'inport': { 'name': 'InPort',
						'type': 'Class',
						'body':
						{
							'name': ('nameattr.string','String')
						}
					},
			'outport': {'name': 'OutPort',
						'type': 'Class',
						'body':
						{
							'name': ('nameattr.string','String')
						}
					},
			'transition': { 'name': 'Transition',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'transition_', ['getNodeId']],
							'target': ('targetattr.string','String'),
							'after': ('afterattr.float','Float'),
							'portname': ('portattr.string','String')
						}
					},
			'after_expression': {
					'name': 'after_expression',
					'type': 'Association',
					'source': { 'name': 'Transition', 'type': 'Transition' },
					'target': { 'name': 'Expression', 'type': 'Expression' },
					'condition': ['direct', '@Transition', '@Expression'],
					'body': {
						'name': ['concat','transition_after_expression_', ['concat','@Transition.id','@Expression.id']]
					}
				},
					
			'event': { 'name': 'Event',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'event_', ['getNodeId']],
							'name': ('namevalue.name','String')
						}
					},
			'guard': { 'name': 'Guard',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'guard_', ['getNodeId']]
						}
					},
			'raise': { 'name': 'Raise',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'raise_', ['getNodeId']]
						}
					},
			'scopeattr': { 'name': 'Scope',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'scopeattr_', ['getNodeId']]
						}
					},
			'targetattr': { 'name': 'Target',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'targetattr_', ['getNodeId']]
						}
					},
			'return_stm': { 'name': 'Return',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'return_', ['getNodeId']]
						}
					},
			'continue_stm': { 'name': 'Continue',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'continue_', ['getNodeId']]
						}
					},
			'break_stm': { 'name': 'Break',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'break_', ['getNodeId']]
						}
					},
			'while_stm': { 'name': 'While',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'while_', ['getNodeId']]
						}
					},
			'ifelse_stm': { 'name': 'IfElse',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'ifelse_', ['getNodeId']]
						}
					},
			'statementbody': {
						'name': 'ActionBlock',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'statementbody_', ['getNodeId']]
						}
					},
			'parexpr': { 'name': 'Parenthesis',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'parexpr_', ['getNodeId']]
						}
					},
			'notexpr': { 'name': 'Not',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'notexpr_', ['getNodeId']]
						}
					},
			'minusexpr': { 'name': 'Minus',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'minusexpr_', ['getNodeId']]
						}
					},
			'andexpr': { 'name': 'And',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'andexpr_', ['getNodeId']]
						}
					},
			'orexpr': { 'name': 'Or',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'orexpr_', ['getNodeId']]
						}
					},
			'equalsexpr': { 'name': 'Equal',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'equalsexpr_', ['getNodeId']]
						}
					},
			'nequalsexpr': { 'name': 'NEqual',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'nequalsexpr_', ['getNodeId']]
						}
					},
			'leqthanexpr': { 'name': 'LEThan',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'leqthanexpr_', ['getNodeId']]
						}
					},
			'lthanexpr': { 'name': 'LThan',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'lthanexpr_', ['getNodeId']]
						}
					},
			'geqthanexpr': { 'name': 'GEThan',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'geqthanexpr_', ['getNodeId']]
						}
					},
			'gthanexpr': { 'name': 'GThan',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'gthanexpr_', ['getNodeId']]
						}
					},
			'modexpr': { 'name': 'Mod',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'modexpr_', ['getNodeId']]
						}
					},
			'divexpr': { 'name': 'Div',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'divexpr_', ['getNodeId']]
						}
					},
			'multexpr': { 'name': 'Mult',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'multexpr_', ['getNodeId']]
						}
					},
			'sumexpr': { 'name': 'Add',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'sumexpr_', ['getNodeId']]
						}
					},
			'subtractionexpr': { 'name': 'Subtract',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'subtractionexpr_', ['getNodeId']]
						}
					},
			'selection': { 'name': 'Selection',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'selection_', ['getNodeId']]
						}
					},
			'dict': { 'name': 'Dict',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'dict_', ['getNodeId']]
						}
					},
			'dictitem': { 'name': 'DictArgument',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'dictitem_', ['getNodeId']]
						}
					},
			'vector': { 'name': 'Array',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'array_', ['getNodeId']]
						}
					},
			'vectoritem': { 'name': 'RegularArgument',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'vectoritem_', ['getNodeId']]
						}
					},
			'tuple': { 'name': 'Tuple',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'tuple_', ['getNodeId']]
						}
					},
			'tuplearg': { 'name': 'RegularArgument',
						'type': 'Class',
						'body':
						{
							'id': ['concat', 'tuplearg_', ['getNodeId']]
						}
					},
			'selfexpression_dotexpression': {
					'name': 'selfexpression_dotexpression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'SelfExpression' },
					'target': { 'name': 'b', 'type': 'AbsNavigationExpression' },
					'condition': ['nextTo', '@a', '@b'],
					'body': {
						'name': ['concat','selfexpression_dotexpression_', ['concat','@a.id','@b.id']]
					}
				},
			'navigationexpression_absnavigationexpression': {
					'name': 'navigationexpression_absnavigationexpression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'NavigationExpression' },
					'target': { 'name': 'b', 'type': 'AbsNavigationExpression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','navigationexpression_absnavigationexpression_', ['concat','@a.id','@b.id']]
					}
				},
			'class_attribute': {
					'name': 'class_attribute',
					'type': 'Association',
					'source': { 'name': 'Class', 'type': 'Class' },
					'target': { 'name': 'Attribute', 'type': 'Attribute' },
					'condition': ['direct', '@Class', '@Attribute'],
					'body': {
						'name': ['concat','class_attribute_', ['concat','@Class.name','@Attribute.name']]
					}
				},
			'class_relationship': {
					'name': 'class_relationship',
					'type': 'Association',
					'source': { 'name': 'Class', 'type': 'Class' },
					'target': { 'name': 'Relationship', 'type': 'Relationship' },
					'condition': ['direct', '@Class', '@Relationship'],
					'body': {
						'name': ['concat','class_relationship_', ['concat','@Class.name','@Relationship.id']]
					}
				},
			'class_inport': {
					'name': 'class_inport',
					'type': 'Association',
					'source': { 'name': 'Class', 'type': 'Class' },
					'target': { 'name': 'InPort', 'type': 'InPort' },
					'condition': ['direct', '@Class', '@InPort'],
					'body': {
						'name': ['concat','class_inport', ['concat','@Class.name','@InPort.name']]
					}
				},
			'transition_inport': {
					'name': 'transition_inport',
					'type': 'Association',
					'source': { 'name': 'Transition', 'type': 'Transition' },
					'target': { 'name': 'InPort', 'type': 'InPort' },
					'condition': ['equals', '@InPort.name', '@Transition.portname'],
					'body': {
						'name': ['concat','transition_inport_', ['concat','@InPort.name','@Transition.id']]
					}
				},
			'transition_event_trigger': {
					'name': 'transition_event_trigger',
					'type': 'Association',
					'source': { 'name': 'Transition', 'type': 'Transition' },
					'target': { 'name': 'Event', 'type': 'Event' },
					'condition': ['direct', '@Transition', '@Event'],
					'body': {
						'name': ['concat','transition_event_trigger_', ['concat','@Transition.id','@Event.id']]
					}
				},
			'transition_guard': {
					'name': 'transition_guard',
					'type': 'Association',
					'source': { 'name': 'Transition', 'type': 'Transition' },
					'target': { 'name': 'Guard', 'type': 'Guard' },
					'condition': ['direct', '@Transition', '@Guard'],
					'body': {
						'name': ['concat','transition_guard', ['concat','@Transition.id','@Guard.id']]
					}
				},
			'transition_raise': {
					'name': 'transition_raise',
					'type': 'Association',
					'source': { 'name': 'Transition', 'type': 'Transition' },
					'target': { 'name': 'Raise', 'type': 'Raise' },
					'condition': ['direct', '@Transition', '@Raise'],
					'body': {
						'name': ['concat','transition_raise_', ['concat','@Transition.id','@Raise.id']]
					}
				},
			'guard_expression': {
					'name': 'guard_expression',
					'type': 'Association',
					'source': { 'name': 'Guard', 'type': 'Guard' },
					'target': { 'name': 'Expression', 'type': 'Expression' },
					'condition': ['direct', '@Guard', '@Expression'],
					'body': {
						'name': ['concat','transition_event_trigger_', ['concat','@Guard.id','@Expression.id']]
					}
				},
			'raise_methodcall': {
					'name': 'raise_methodcall',
					'type': 'Association',
					'source': { 'name': 'Raise', 'type': 'Raise' },
					'target': { 'name': 'MethodCall', 'type': 'MethodCall' },
					'condition': ['direct', '@Raise', '@MethodCall'],
					'body': {
						'name': ['concat','raise_methodcall_', ['concat','@Raise.id','@MethodCall.id']]
					}
				},
			'raise_scope': {
					'name': 'raise_scope',
					'type': 'Association',
					'source': { 'name': 'Raise', 'type': 'Raise' },
					'target': { 'name': 'Scope', 'type': 'Scope' },
					'condition': ['direct', '@Raise', '@Scope'],
					'body': {
						'name': ['concat','raise_scope_', ['concat','@Raise.id','@Scope.id']]
					}
				},
			'raise_target': {
					'name': 'raise_target',
					'type': 'Association',
					'source': { 'name': 'Raise', 'type': 'Raise' },
					'target': { 'name': 'Target', 'type': 'Target' },
					'condition': ['direct', '@Raise', '@Target'],
					'body': {
						'name': ['concat','raise_target_', ['concat','@Raise.id','@Target.id']]
					}
				},
			'scope_expression': {
					'name': 'scope_expression',
					'type': 'Association',
					'source': { 'name': 'Scope', 'type': 'Scope' },
					'target': { 'name': 'Expression', 'type': 'Expression' },
					'condition': ['direct', '@Scope', '@Expression'],
					'body': {
						'name': ['concat','scope_expression_', ['concat','@Scope.id','@Expression.id']]
					}
				},
			'target_expression': {
					'name': 'target_expression',
					'type': 'Association',
					'source': { 'name': 'Target', 'type': 'Target' },
					'target': { 'name': 'Expression', 'type': 'Expression' },
					'condition': ['direct', '@Target', '@Expression'],
					'body': {
						'name': ['concat','target_expression_', ['concat','@Target.id','@Expression.id']]
					}
				},
			'actionblock_statement': {
					'name': 'actionblock_statement',
					'type': 'Association',
					'source': { 'name': 'ActionBlock', 'type': 'ActionBlock' },
					'target': { 'name': 'Statement', 'type': 'Statement' },
					'condition': ['first', '@ActionBlock', '@Statement'],
					'body': {
						'name': ['concat','actionblock_statement_', ['concat','@ActionBlock.id','@Statement.id']]
					}
				},
			'statement_statement_next': {
					'name': 'statement_statement_next',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Statement' },
					'target': { 'name': 'b', 'type': 'Statement' },
					'condition': ['nextTo', '@a', '@b'],
					'body': {
						'name': ['concat','statement_statement_next_', ['concat','@a.id','@b.id']]
					}
				},
			'class_statemachine': {
					'name': 'class_statemachine',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Class' },
					'target': { 'name': 'b', 'type': 'StateMachine' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','class_statemachine_', ['concat','@a.name','@b.id']]
					}
				},
			'statemachine_absstate': {
					'name': 'statemachine_absstate',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'StateMachine' },
					'target': { 'name': 'b', 'type': 'AbsState' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','statemachine_absstate_', ['concat','@a.id','@b.id']]
					}
				},
			'statemachine_pseudostate': {
					'name': 'statemachine_pseudostate',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'StateMachine' },
					'target': { 'name': 'b', 'type': 'PseudoState' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','statemachine_pseudostate_', ['concat','@a.id','@b.id']]
					}
				},
			'absstate_absstate_inner': {
					'name': 'absstate_absstate_inner',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsState' },
					'target': { 'name': 'b', 'type': 'AbsState' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absstate_absstate_inner_', ['concat','@a.id','@b.id']]
					}
				},
			'statemachine_transition': {
					'name': 'statemachine_transition',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'StateMachine' },
					'target': { 'name': 'b', 'type': 'Transition' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','statemachine_transition', ['concat','@a.id','@b.id']]
					}
				},
			'absstate_transition': {
					'name': 'absstate_transition',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsState' },
					'target': { 'name': 'b', 'type': 'Transition' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absstate_transition_', ['concat','@a.id','@b.id']]
					}
				},
			'absstate_pseudostate': {
					'name': 'absstate_pseudostate',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsState' },
					'target': { 'name': 'b', 'type': 'PseudoState' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absstate_pseudostate_', ['concat','@a.id','@b.id']]
					}
				},
			'class_method': {
					'name': 'class_method',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Class' },
					'target': { 'name': 'b', 'type': 'AbsMethod' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','class_method_', ['concat','@a.name','@b.id']]
					}
				},
			'absmethod_body': {
					'name': 'absmethod_actionblock_body',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsMethod' },
					'target': { 'name': 'b', 'type': 'ActionBlock' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absmethod_actionblock_body', ['concat','@a.id','@b.id']]
					}
				},
			'methodcall_sender': {
					'name': 'methodcall_sender',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsMethodCall' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','methodcall_sender', ['concat','@a.id','@b.id']]
					}
				},
			'methodcall_argument': {
					'name': 'methodcall_argument',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsMethodCall' },
					'target': { 'name': 'b', 'type': 'Argument' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','methodcall_argument_', ['concat','@a.id','@b.id']]
					}
				},
			'argument_value': {
					'name': 'argument_value',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Argument' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','argument_value_', ['concat','@a.id','@b.id']]
					}
				},
			'argument_argument_next': {
					'name': 'argument_argument_next',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Argument' },
					'target': { 'name': 'b', 'type': 'Argument' },
					'condition': ['nextTo', '@a', '@b'],
					'body': {
						'name': ['concat','argument_argument_next_', ['concat','@a.id','@b.id']]
					}
				},
			'declaration_navigationexpression_type': {
					'name': 'declaration_navigationexpression_type',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Declaration' },
					'target': { 'name': 'b', 'type': 'NavigationExpression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','declaration_navigationexpression_type_', ['concat','@a.id','@b.id']]
					}
				},
			'declaration_expression_init': {
					'name': 'declaration_expression_init',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Declaration' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['second', '@a', '@b'],
					'body': {
						'name': ['concat','declaration_expression_init_', ['concat','@a.id','@b.id']]
					}
				},
			'event_parameter': {
					'name': 'event_parameter',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Event' },
					'target': { 'name': 'b', 'type': 'Parameter' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','event_parameter_', ['concat','@a.id','@b.id']]
					}
				},
			'absmethod_parameter': {
					'name': 'absmethod_parameter',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsMethod' },
					'target': { 'name': 'b', 'type': 'Parameter' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','absmethod_parameter_', ['concat','@a.id','@b.id']]
					}
				},
			'parameter_parameter_next': {
					'name': 'parameter_parameter_next',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Parameter' },
					'target': { 'name': 'b', 'type': 'Parameter' },
					'condition': ['nextTo', '@a', '@b'],
					'body': {
						'name': ['concat','parameter_parameter_next_', ['concat','@a.id','@b.id']]
					}
				},
			'parameter_type_expression': {
					'name': 'parameter_type_expression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Parameter' },
					'target': { 'name': 'b', 'type': 'NavigationExpression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','parameter_type_expression_', ['concat','@a.id','@b.id']]
					}
				},
			'assignment_expression_left': {
					'name': 'assignment_expression_left',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Assignment' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','assignment_expression_left_', ['concat','@a.id','@b.id']]
					}
				},
			'assignment_expression_right': {
					'name': 'assignment_expression_right',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Assignment' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['second', '@a', '@b'],
					'body': {
						'name': ['concat','assignment_expression_right_', ['concat','@a.id','@b.id']]
					}
				},
			'while_expression_condition': {
					'name': 'while_expression_condition',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'While' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','while_expression_condition_', ['concat','@a.id','@b.id']]
					}
				},
			'while_body': {
					'name': 'while_actionblock_body',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'While' },
					'target': { 'name': 'b', 'type': 'ActionBlock' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','while_actionblock_body_', ['concat','@a.id','@b.id']]
					}
				},
			'ifelse_expression_condition': {
					'name': 'ifelse_expression_condition',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'IfElse' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','ifelse_expression_condition_', ['concat','@a.id','@b.id']]
					}
				},
			'if_body': {
					'name': 'ifelse_actionblock_ifbody',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'IfElse' },
					'target': { 'name': 'b', 'type': 'ActionBlock' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','ifelse_actionblock_ifbody_', ['concat','@a.id','@b.id']]
					}
				},
			'else_body': {
					'name': 'ifelse_actionblock_elsebody',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'IfElse' },
					'target': { 'name': 'b', 'type': 'ActionBlock' },
					'condition': ['second', '@a', '@b'],
					'body': {
						'name': ['concat','ifelse_actionblock_elsebody_', ['concat','@a.id','@b.id']]
					}
				},
			'transition_actionblock': {
					'name': 'transition_actionblock',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Transition' },
					'target': { 'name': 'b', 'type': 'ActionBlock' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','transition_actionblock_', ['concat','@a.id','@b.id']]
					}
				},
			'absstate_onenter': {
					'name': 'absstate_onenter',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsState' },
					'target': { 'name': 'b', 'type': 'OnEnter' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absstate_onenter_', ['concat','@a.id','@b.id']]
					}
				},
			'absstate_onexit': {
					'name': 'absstate_onexit',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'AbsState' },
					'target': { 'name': 'b', 'type': 'OnExit' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','absstate_onexit_', ['concat','@a.id','@b.id']]
					}
				},
			'binop_expression_left': {
					'name': 'binop_expression_left',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Binop' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','binop_expression_left_', ['concat','@a.id','@b.id']]
					}
				},
			'binop_expression_right': {
					'name': 'binop_expression_right',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Binop' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['second', '@a', '@b'],
					'body': {
						'name': ['concat','binop_expression_right_', ['concat','@a.id','@b.id']]
					}
				},
			'composite_compositeargument': {
					'name': 'composite_compositeargument',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Composite' },
					'target': { 'name': 'b', 'type': 'CompositeArgument' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','composite_compositeargument_', ['concat','@a.id','@b.id']]
					}
				},
			'regularargument_expression': {
					'name': 'regularargument_expression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'RegularArgument' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['direct', '@a', '@b'],
					'body': {
						'name': ['concat','regularargument_expression_', ['concat','@a.id','@b.id']]
					}
				},
			'dictargument_expression': {
					'name': 'dictargument_expression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'DictArgument' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['second', '@a', '@b'],
					'body': {
						'name': ['concat','dictargument_expression_', ['concat','@a.id','@b.id']]
					}
				},
			'dictargument_labelexpression': {
					'name': 'dictargument_labelexpression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'DictArgument' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','dictargument_labelexpression_', ['concat','@a.id','@b.id']]
					}
				},
			'compositeargument_compositeargument_next': {
					'name': 'compositeargument_compositeargument_next',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'CompositeArgument' },
					'target': { 'name': 'b', 'type': 'CompositeArgument' },
					'condition': ['nextTo', '@a', '@b'],
					'body': {
						'name': ['concat','compositeargument_compositeargument_next_', ['concat','@a.id','@b.id']]
					}
				},
			'unop_expression': {
					'name': 'unop_expression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Unop' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','unop_expression_', ['concat','@a.id','@b.id']]
					}
				},
			'return_expression': {
					'name': 'return_expression',
					'type': 'Association',
					'source': { 'name': 'a', 'type': 'Return' },
					'target': { 'name': 'b', 'type': 'Expression' },
					'condition': ['first', '@a', '@b'],
					'body': {
						'name': ['concat','return_expression_', ['concat','@a.id','@b.id']]
					}
				}
		}

