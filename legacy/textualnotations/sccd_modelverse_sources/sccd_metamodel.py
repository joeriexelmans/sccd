# -*- coding: utf-8 -*-

from mvk.impl.python.constants import CreateConstants, UpdateConstants
from mvk.impl.python.datatype import TypeFactory, Type, IntegerType, StringType, \
	BooleanType, FloatType
from mvk.impl.python.datavalue import MappingValue, \
	LocationValue, StringValue, FloatValue, \
	IntegerValue, BooleanValue, InfiniteValue, Iterator
from mvk.impl.python.object import ClabjectReference, Clabject
from mvk.mvk import MvK

class Gen():

	def __init__(self):
		self.mvk = MvK()

	def instance(self):
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('SimpleClassDiagrams.name'): StringValue('SCCD')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('author'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('description'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType(),
			StringValue('Attribute.default'): StringValue('')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('MethodCallStm')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Not')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Mod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('While')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('GEThan')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Inheritance')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Inheritance'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('priority'),
			StringValue('Attribute.type'): IntegerType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('State')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('DictArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('AbsMethod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Target')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Selection')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('AtomValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Top')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Parenthesis')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Import')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Import'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('as'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Import'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('from'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Import'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('location'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Method')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Method'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('returnType'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Method'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('StateMachine')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Declaration')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Declaration'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Composition')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('OrthogonalComponent')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('DotExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.DotExpression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('path'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('And')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Dict')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('AbsState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.AbsState'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('IfElse')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('AbsNavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('AbsMethodCall')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.AbsMethodCall'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Continue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Return')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('ID'),
			StringValue('Class.id_field'): StringValue('ID.id')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.ID'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('id'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Named'),
			StringValue('Class.id_field'): StringValue('Named.name')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Named'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Guard')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Raise')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Bottom')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Scope')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('MethodCall')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Assignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Or')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('LThan')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('LEThan')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('BooleanValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.BooleanValue'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('value'),
			StringValue('Attribute.type'): BooleanType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Mult')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('RegularArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('GThan')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Div')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Minus')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('InPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('OutPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('CompositeArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('FinalState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('PlainAssignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('StringValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.StringValue'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('value'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Event')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Event'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('FloatValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.FloatValue'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('value'),
			StringValue('Attribute.type'): FloatType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('OnExit')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Destructor')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Parameter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Parameter'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('default'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Parameter'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('OnEnter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Relationship')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Relationship'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('max'),
			StringValue('Attribute.type'): IntegerType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Relationship'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('class'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Relationship'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('min'),
			StringValue('Attribute.type'): IntegerType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Class')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Class'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('default'),
			StringValue('Attribute.type'): BooleanType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Tuple')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Argument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Argument'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Composite')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Add')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('IntegerValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.IntegerValue'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('value'),
			StringValue('Attribute.type'): IntegerType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('NavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Aggregation')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Break')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Association')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Association'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Transition')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Transition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('default'),
			StringValue('Attribute.type'): BooleanType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Transition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('target'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('NEqual')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('MinusAssignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.PseudoState'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Attribute')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Attribute'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('default'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.Attribute'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('type'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Subtract')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('SelfExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('PlusAssignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('HistoryState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.HistoryState'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('isDeepHistory'),
			StringValue('Attribute.type'): BooleanType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Equal')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Constructor')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(True),
			StringValue('Class.name'): StringValue('Unop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('InitialState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Class'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Class.name'): StringValue('Array')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('MethodCall_i_AbsMethodCall'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.MethodCall'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethodCall')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Not_i_Unop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Not'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Unop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_statement'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('statement_statement_next'),
			StringValue('Association.to_port'): StringValue('to_statement'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('statement_statement_next.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Statement'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.statement_statement_next'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('While_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.While'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absstate'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absstate_pseudostate'),
			StringValue('Association.to_port'): StringValue('to_pseudostate'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absstate_pseudostate.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absstate_pseudostate'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('MethodCall_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.MethodCall'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Subtract_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Subtract'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Dict_i_Composite'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Dict'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Composite')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Unop_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Unop'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('BooleanValue_i_AtomValue'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.BooleanValue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AtomValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Parenthesis_i_Unop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Parenthesis'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Unop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Raise_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Raise'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_raise'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('raise_scope'),
			StringValue('Association.to_port'): StringValue('to_scope'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('raise_scope.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Raise'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Scope')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.raise_scope'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('FinalState_i_PseudoState'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.FinalState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('NEqual_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.NEqual'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('AbsNavigationExpression_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsNavigationExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_ifelse'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('ifelse_expression_condition'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('ifelse_expression_condition.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.IfElse'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.ifelse_expression_condition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('AbsMethod_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsMethod'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('GEThan_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.GEThan'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Class_i_Named'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Named')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_while'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('while_actionblock_body'),
			StringValue('Association.to_port'): StringValue('to_actionblock'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('while_actionblock_body.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.While'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.while_actionblock_body'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('StateMachine_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.StateMachine'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('OnEnter_i_ActionBlock'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.OnEnter'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absstate'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absstate_absstate_inner'),
			StringValue('Association.to_port'): StringValue('to_absstate'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absstate_absstate_inner.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absstate_absstate_inner'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('GThan_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.GThan'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_scope'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('scope_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('scope_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Scope'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.scope_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_ifelse'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('ifelse_actionblock_elsebody'),
			StringValue('Association.to_port'): StringValue('to_actionblock'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('ifelse_actionblock_elsebody.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.IfElse'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.ifelse_actionblock_elsebody'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('PlusAssignment_i_Assignment'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.PlusAssignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Assignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('AtomValue_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AtomValue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Selection_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Selection'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_assignment'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('assignment_expression_right'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('assignment_expression_right.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Assignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.assignment_expression_right'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absmethod'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absmethod_parameter'),
			StringValue('Association.to_port'): StringValue('to_parameter'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absmethod_parameter.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsMethod'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Parameter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absmethod_parameter'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_statemachine'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('statemachine_transition'),
			StringValue('Association.to_port'): StringValue('to_transition'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('statemachine_transition.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.StateMachine'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Transition')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.statemachine_transition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('ActionBlock_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.ActionBlock'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_raise'),
			StringValue('Association.to_port'): StringValue('to_raise'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_raise.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Raise')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_raise'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_target'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('target_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('target_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Target'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.target_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_while'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('while_expression_condition'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('while_expression_condition.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.While'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.while_expression_condition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('InitialState_i_PseudoState'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.InitialState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Binop_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Binop'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('InPort_i_Named'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.InPort'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Named')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('OutPort_i_Named'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.OutPort'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Named')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Expression_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Expression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Array_i_Composite'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Array'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Composite')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('NavigationExpression_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.NavigationExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_actionblock'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('actionblock_statement'),
			StringValue('Association.to_port'): StringValue('to_statement'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('actionblock_statement.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.ActionBlock'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.actionblock_statement'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Relationship_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Relationship'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Add_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Add'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Inheritance_i_Relationship'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Inheritance'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Relationship')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Import_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Import'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Constructor_i_AbsMethod'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Constructor'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_regularargument'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('regularargument_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('regularargument_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.RegularArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.regularargument_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Minus_i_Unop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Minus'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Unop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Method_i_AbsMethod'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Method'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('after_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('after_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.after_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_assignment'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('assignment_expression_left'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('assignment_expression_left.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Assignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.assignment_expression_left'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_inport'),
			StringValue('Association.to_port'): StringValue('to_inport'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_inport.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.InPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_inport'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_outport'),
			StringValue('Association.to_port'): StringValue('to_outport'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_outport.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.OutPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_outport'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('MinusAssignment_i_Assignment'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.MinusAssignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Assignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_relationship'),
			StringValue('Association.to_port'): StringValue('to_relationship'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_relationship.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Relationship')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_relationship'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Mult_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Mult'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('DotExpression_i_AbsNavigationExpression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.DotExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsNavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('PseudoState_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.PseudoState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Bottom_i_ActionBlock'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Bottom'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_attribute'),
			StringValue('Association.to_port'): StringValue('to_attribute'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_attribute.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Attribute')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_attribute'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Scope_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Scope'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Assignment_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Assignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Destructor_i_AbsMethod'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Destructor'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Equal_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Equal'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_statemachine'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('statemachine_absstate'),
			StringValue('Association.to_port'): StringValue('to_absstate'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('statemachine_absstate.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.StateMachine'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.statemachine_absstate'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Parameter_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Parameter'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('OrthogonalComponent_i_AbsState'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.OrthogonalComponent'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Return_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Return'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Statement_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Statement'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_raise'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('raise_methodcall'),
			StringValue('Association.to_port'): StringValue('to_methodcall'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('raise_methodcall.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Raise'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.MethodCall')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.raise_methodcall'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_argument'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('argument_argument_next'),
			StringValue('Association.to_port'): StringValue('to_argument'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('argument_argument_next.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Argument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Argument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.argument_argument_next'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_raise'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('raise_target'),
			StringValue('Association.to_port'): StringValue('to_Target'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('raise_target.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Raise'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Target')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.raise_target'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Composition_i_Relationship'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Composition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Relationship')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_return'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('return_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('return_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Return'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.return_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_parameter'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('parameter_parameter_next'),
			StringValue('Association.to_port'): StringValue('to_parameter'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('parameter_parameter_next.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Parameter'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Parameter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.parameter_parameter_next'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('OnExit_i_ActionBlock'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.OnExit'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absstate'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absstate_onexit'),
			StringValue('Association.to_port'): StringValue('to_onexit'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absstate_onexit.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.OnExit')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absstate_onexit'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('State_i_AbsState'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.State'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_statemachine'),
			StringValue('Association.to_port'): StringValue('to_statemachine'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_statemachine.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.StateMachine')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_statemachine'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_binop'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('binop_expression_right'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('binop_expression_right.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Binop'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.binop_expression_right'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_actionblock'),
			StringValue('Association.to_port'): StringValue('to_actionblock'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_actionblock.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_actionblock'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_regularargument'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('dictargument_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('dictargument_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.DictArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.dictargument_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('IntegerValue_i_AtomValue'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.IntegerValue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AtomValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_declaration'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('declaration_navigationexpression_type'),
			StringValue('Association.to_port'): StringValue('to_navigationexpression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('declaration_navigationexpression_type.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Declaration'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.NavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.declaration_navigationexpression_type'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('RegularArgument_i_CompositeArgument'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.RegularArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_argument'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('argument_value'),
			StringValue('Association.to_port'): StringValue('to_value'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('argument_value.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Argument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.argument_value'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('MethodCallStm_i_AbsMethodCall'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.MethodCallStm'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethodCall')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('HistoryState_i_PseudoState'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.HistoryState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_statemachine'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('statemachine_pseudostate'),
			StringValue('Association.to_port'): StringValue('to_pseudostate'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('statemachine_pseudostate.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.StateMachine'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.PseudoState')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.statemachine_pseudostate'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('MethodCallStm_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.MethodCallStm'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('LEThan_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.LEThan'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Composite_i_Expression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Composite'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_methodcall'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('methodcall_sender'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('methodcall_sender.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsMethodCall'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.methodcall_sender'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('IfElse_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.IfElse'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_binop'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('binop_expression_left'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('binop_expression_left.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Binop'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.binop_expression_left'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Event_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Event'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_method'),
			StringValue('Association.to_port'): StringValue('to_method'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_method.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsMethod')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_method'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('LThan_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.LThan'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Attribute_i_Named'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Attribute'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Named')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_guard'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('guard_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('guard_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Guard'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.guard_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_unop'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('unop_expression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('unop_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Unop'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.unop_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Tuple_i_Composite'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Tuple'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Composite')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Continue_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Continue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Declaration_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Declaration'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_ifelse'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('ifelse_actionblock_ifbody'),
			StringValue('Association.to_port'): StringValue('to_actionblock'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('ifelse_actionblock_ifbody.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.IfElse'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.ifelse_actionblock_ifbody'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absstate'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absstate_onenter'),
			StringValue('Association.to_port'): StringValue('to_onenter'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absstate_onenter.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.OnEnter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absstate_onenter'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('StringValue_i_AtomValue'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.StringValue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AtomValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Div_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Div'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_compositeargument'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('compositeargument_compositeargument_next'),
			StringValue('Association.to_port'): StringValue('to_compositeargument'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('compositeargument_compositeargument_next.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.compositeargument_compositeargument_next'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Transition_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('FloatValue_i_AtomValue'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.FloatValue'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AtomValue')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absstate'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('absstate_transition'),
			StringValue('Association.to_port'): StringValue('to_transition'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absstate_transition.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Transition')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absstate_transition'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_navigationexpression'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('navigationexpression_absnavigationexpression'),
			StringValue('Association.to_port'): StringValue('to_absnavigationexpression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('navigationexpression_absnavigationexpression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.NavigationExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsNavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.navigationexpression_absnavigationexpression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('DictArgument_i_CompositeArgument'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.DictArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Association_i_Relationship'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Association'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Relationship')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('SelfExpression_i_AbsNavigationExpression'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.SelfExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.AbsNavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_guard'),
			StringValue('Association.to_port'): StringValue('to_guard'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_guard.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Guard')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_guard'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Guard_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Guard'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Or_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Or'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_inport'),
			StringValue('Association.to_port'): StringValue('to_inport'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_inport.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.InPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_inport'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_class'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('class_outport'),
			StringValue('Association.to_port'): StringValue('to_outport'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('class_outport.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Class'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.OutPort')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.class_outport'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): InfiniteValue('inf'),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_methodcall'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('methodcall_argument'),
			StringValue('Association.to_port'): StringValue('to_argument'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('methodcall_argument.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsMethodCall'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Argument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.methodcall_argument'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_composite'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('composite_compositeargument'),
			StringValue('Association.to_port'): StringValue('to_compositeargument'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('composite_compositeargument.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Composite'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.composite_compositeargument'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_parameter'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('parameter_type_expression'),
			StringValue('Association.to_port'): StringValue('to_type_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('parameter_type_expression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Parameter'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.NavigationExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.parameter_type_expression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('AbsState_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsState'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('PlainAssignment_i_Assignment'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.PlainAssignment'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Assignment')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_dictargument'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('dictargument_labelexpression'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('dictargument_labelexpression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.DictArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.dictargument_labelexpression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Argument_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Argument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_absmethod'),
			StringValue('Association.to_min'): IntegerValue(1),
			StringValue('Class.name'): StringValue('absmethod_actionblock_body'),
			StringValue('Association.to_port'): StringValue('to_actionblock'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('absmethod_actionblock_body.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.AbsMethod'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.absmethod_actionblock_body'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_event'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('event_parameter'),
			StringValue('Association.to_port'): StringValue('to_parameter'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('event_parameter.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Event'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Parameter')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.event_parameter'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Break_i_Statement'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Break'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Statement')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('And_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.And'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Top_i_ActionBlock'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Top'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ActionBlock')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_transition'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('transition_event_trigger'),
			StringValue('Association.to_port'): StringValue('to_event'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('transition_event_trigger.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Transition'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Event')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.transition_event_trigger'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_selfexpression'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('selfexpression_dotexpression'),
			StringValue('Association.to_port'): StringValue('to_dotexpression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('selfexpression_dotexpression.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.SelfExpression'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.DotExpression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.selfexpression_dotexpression'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Mod_i_Binop'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Mod'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Binop')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('CompositeArgument_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.CompositeArgument'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Association'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Association.to_max'): IntegerValue(1),
			StringValue('Association.from_max'): InfiniteValue('inf'),
			StringValue('Association.from_port'): StringValue('from_declaration'),
			StringValue('Association.to_min'): IntegerValue(0),
			StringValue('Class.name'): StringValue('declaration_expression_init'),
			StringValue('Association.to_port'): StringValue('to_expression'),
			StringValue('Class.is_abstract'): BooleanValue(False),
			StringValue('Association.from_min'): IntegerValue(0),
			StringValue('Class.id_field'): StringValue('declaration_expression_init.name'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Declaration'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Expression')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Attribute'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD.declaration_expression_init'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Attribute.name'): StringValue('name'),
			StringValue('Attribute.type'): StringType()})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Target_i_ID'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Target'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.ID')})
		}))
		cl = self.mvk.create(MappingValue({
			CreateConstants.TYPE_KEY: LocationValue('protected.formalisms.SimpleClassDiagrams.Inheritance'),
			CreateConstants.LOCATION_KEY: LocationValue('protected.formalisms.SCCD'),
			CreateConstants.ATTRS_KEY: MappingValue({
			StringValue('Inheritance.name'): StringValue('Aggregation_i_Relationship'),
			StringValue('from_class'): LocationValue('protected.formalisms.SCCD.Aggregation'),
			StringValue('to_class'): LocationValue('protected.formalisms.SCCD.Relationship')})
		}))
