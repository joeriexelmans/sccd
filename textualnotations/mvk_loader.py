from io import open
import os
import re
import sys
from plyplus import grammars
from plyplus import Grammar
from plyplus.plyplus import TokValue
from plyplus.strees import Str
from plyplus.strees import STree
import copy

import time

from mvk.impl.python.constants import CreateConstants, UpdateConstants
from mvk.impl.python.datatype import TypeFactory, Type, IntegerType, StringType, \
	BooleanType, FloatType
from mvk.impl.python.datavalue import MappingValue, \
	LocationValue, StringValue, FloatValue, \
	IntegerValue, BooleanValue, InfiniteValue, Iterator

from mvk.impl.python.object import ClabjectReference, Clabject

from mvk.mvk import MvK

import mvk

from sccd_asg_mapper import SCCD_ASG_Mapper

pathname = os.path.dirname(os.path.realpath(__file__))

#from shell import Shell
from sccd_modelverse_sources.sccd_metamodel import Gen as GenSCCD

DEBUG = False
JUST_TESTS = False
CALL_TESTS = False

def debug(defname, var):
	if(DEBUG is False or var is None):
		return
	if(var.is_success()):
		print('\t' + defname + ': is_success() = True')
	else:
		print('\t' + defname + ': is_success() = False')
		print var.get_status_message()

def debug_print(_str_):
	if(DEBUG is False):
		return
	print(_str_)


def isType(v):
	return isinstance(v, Type)

def isStringValue(v):
	return (isinstance(v, StringValue) or
				isinstance(v, LocationValue) or
				isinstance(v, InfiniteValue))

class ClassRepresenter(object):
	def __init__(self, name, ident, idlist, parent, body):
		self.name = name
		self.id = ident
		self.children = idlist
		self.parent = parent
		self.body = body
		self.classname = ''
		self.super = []
		debug_print('elem: ' + self.typestring() + '(' + self.name + ', ' + str(self.id) +') ' +
						str(self.children))

	def fillDynamicAttributes(self, context):
		for key in self.body:
			if(isinstance(self.body[key],list)):
				self.body.update({
					key:context.evaluate_statement(
						None,
						{'source': self, 'target': self},
						self.body[key])}
				)

	def fillSuperTypes(self, context):
		location = context.location + '.' + self.name
		rl = context.mvk.read(LocationValue(location))
		if(not rl.is_success()):
			raise Exception('Invalid location: ' + str(location))

		item = rl.get_item()
		iterator  = Iterator(item.get_all_super_classes())
		while(iterator.has_next()):
			itemin = iterator.next()
			debug_print('storesupertypes: ' + str(itemin.get_location()))
			lastname = re.compile('\w+').findall(str(itemin.get_location())).pop()
			debug_print('lastname: ' + lastname)
			self.super.append(lastname)

	def typestring(self):
		return 'ClassRepresenter'

	def store(self, context, target):

		location = context.location + '.' + self.name
		self.create(context.mvk, MappingValue({CreateConstants.TYPE_KEY: LocationValue(location),
			CreateConstants.LOCATION_KEY: LocationValue(target),
			CreateConstants.ATTRS_KEY: MappingValue(
				self.buildDict(context.mvk, target, location, self.body)
			)}))

		key = self.getIdField(context, target, location)
		element = target + '.' + str(self.body[key])
		self.classname = element

	def getNthOfType(self, context, index, typename):
		searchid = 0
		for childid in self.children:
			child = context.get_class_by_id(childid)
			if(child.name == typename or typename in child.super):
				if(searchid == index):
					return childid
				else:
					searchid += 1

		return -1 ## meaning: not found

	def getIndexOfChildIdWithType(self, context, ident, typename):
		index = 0

		for childid in self.children:
			child = context.get_class_by_id(childid)
			if(child.name == typename or typename in child.super):
				if(child.id == ident):
					return index
				else:
					index += 1

		return -1 ## meaning: not found

	def create(self, modelverse, mv):
		self.write_call('create', mv)
		if(JUST_TESTS is True):
			return None
		return modelverse.create(mv)

	def getAllAttributes(self, modelverse, typename):
		attributes = {}
		#debug_print(typename)
		lastname = re.compile('\w+').findall(typename).pop()

		#debug_print(typename)
		cl = modelverse.read(LocationValue(typename))
		if(cl.is_success() == False):
			raise Exception('getAllAttributes: Object not found: ' + typename)
		item = cl.get_item()

		iterator  = Iterator(item.get_attributes())
		while(iterator.has_next()):
			attribute = iterator.next()
			name = attribute.get_name()
			typevalue = attribute.get_type()
			attributes.update({str(name): (lastname,str(typevalue))})

		if(isinstance(item, mvk.interfaces.object.Clabject)):
			iterator  = Iterator(item.get_all_super_classes())
			while(iterator.has_next()):
				itemin = iterator.next()
				innerattrs = self.getAllAttributes(modelverse, str(itemin.get_location()))
				attributes = dict(innerattrs.items() + attributes.items())

		return attributes

	def getMvKValue(self, location, attrtype, attrvalue):
		## single types
		if(attrtype == 'IntegerType'):
			return IntegerValue(int(attrvalue))
		if(attrtype == 'FloatType'):
			return FloatValue(float(attrvalue))
		if(attrtype == 'StringType'):
			return StringValue(str(attrvalue))
		if(attrtype == 'BooleanType'):
			if attrvalue == "True":
				return BooleanValue(bool(True))
			else:
				return BooleanValue(bool(False))
		if(attrtype == 'Type'):
			return TypeFactory.get_type(str(attrvalue + 'Type'))

		return LocationValue(attrvalue)

	def buildDict(self, mvk, location, typename, attributes):
		attribute_dict = {}
		attributes_from_type = self.getAllAttributes(mvk, typename)
		for key in attributes:
			if(not isinstance(attributes[key],tuple)): ## ignore unparsed values
				if(key in attributes_from_type): ## also ignore inexisting keys on type (decoration only)
					dict_key = attributes_from_type[key][0] + '.' + key
					attribute_dict.update({
						StringValue(dict_key)
						:
						self.getMvKValue(location, attributes_from_type[key][1], attributes[key])
					})
		return attribute_dict

	def write_call(self, name, mv):
			if(CALL_TESTS is False):
				return
			typename = str(mv[CreateConstants.TYPE_KEY])
			location = str(mv[CreateConstants.LOCATION_KEY])
			attr_it = mv[CreateConstants.ATTRS_KEY].__iter__()
			attrs = '\t\t\t\t'
			while attr_it.has_next():
				k = attr_it.next()
				v = mv[CreateConstants.ATTRS_KEY][k]
				ktype = k.__class__.__name__
				if isStringValue(k):
					attrs = attrs + ktype + '(\'' + str(k) + '\'): '
				else:
					attrs = attrs + ktype + '(' + str(k) + '): '
				vtype = v.__class__.__name__
				if(isType(v)):
					if(isinstance(v, ClabjectReference)):
						attrs = attrs + vtype + '(LocationValue(\'' + str(v.get_path()) + '\'))'
					else:
						if(isinstance(v, Clabject)):
							attrs = attrs + str(v)
						else:
							attrs = attrs + vtype + '()'
				else:
					if isStringValue(v):
						attrs = attrs + vtype + '(\'' + str(v) + '\')'
					else:
						attrs = attrs + vtype + '(' + str(v) + ')'
				if(attr_it.has_next()):
					attrs = attrs + ',\n\t\t\t\t'
				else:
					attrs = attrs + '\n'
	
			p = '\t\tcl = self.mvk.' + name + '(MappingValue({\n'
			p = p + '\t\t\tCreateConstants.TYPE_KEY: LocationValue(\'' + typename + '\'),\n'
			p = p + '\t\t\tCreateConstants.LOCATION_KEY: LocationValue(\'' + location + '\'),\n'
			p = p + '\t\t\tCreateConstants.ATTRS_KEY: MappingValue({\n'
			p = p + attrs
			p = p + '\t\t\t})\n'
			p = p + '\t\t}))\n'
			p = p + '\t\tif(cl.is_success()):\n'
			p = p + '\t\t\tprint(\'\\t: cl.is_success() = True\')\n'
			p = p + '\t\telse:\n'
			p = p + '\t\t\tprint(\'\\t: cl.is_success() = False\')\n'
			p = p + '\t\t\tprint(cl.get_status_message())\n'
			print p

	def resolveTypename(self, context, location, typename):
		rl = context.mvk.read(LocationValue(typename))
		if(not rl is None and not rl.is_success()):
			prevtypename = typename

			while(True):
				rl = context.mvk.read(LocationValue(location))
				if(not rl.is_success()):
					raise RuntimeError('Location ' + location + ' not found while resolving typename: ' + prevtypename)
				if(isinstance(rl.get_item(), mvk.interfaces.object.Model)):
					typename = str(rl.get_item().typed_by().get_path()) + '.' + typename
					break
				else:
					tmploc = re.compile('\w+').findall(location)
					tmploc.pop()
					if(len(tmploc) == 0):
						typename = location + '.' + typename
						break
					else:
						location = '.'.join(tmploc)

			rl = context.mvk.read(LocationValue(typename))
			if(not rl.is_success()):
				raise RuntimeError('Type not found: ' + prevtypename)

		return typename

	def getIdField(self, context, location, typename):
		typename = self.resolveTypename(context, location, typename)

		rl = context.mvk.read(LocationValue(typename))
		try:
			id_field = str(rl.get_item().get_attribute(StringValue('Class.id_field')).get_value())
			#debug_print('IDFIELD: ' + id_field)
			id_field = re.compile('\w+').findall(id_field).pop()
			return id_field
		except Exception:
			#debug_print('default IDFIELD: name')
			return 'name'

class ModelRepresenter(ClassRepresenter):
	def __init__(self, name, ident, idlist, body):
		self.name = name
		self.id = self.parent = ident
		self.children = idlist
		self.body = body
		self.modelname = ''
		self.super = []
		

	def typestring(self):
		return 'ModelRepresenter'

	def store(self, context, target):
		location = context.location
		self.create(context.mvk, MappingValue({CreateConstants.TYPE_KEY: LocationValue(location),
			CreateConstants.LOCATION_KEY: LocationValue(target),
			CreateConstants.ATTRS_KEY: MappingValue(
				self.buildDict(context.mvk, target, location, self.body)
			)}))

		key = self.getIdField(context, target, location)
		self.modelname = str(self.body[key])

class AssociationRepresenter(ClassRepresenter):
	def __init__(self, name, body, fromid, toid):
		self.name = name
		self.body = body
		self.id = self.parent = 0
		self.children = []
		self.super = []
		self.from_node = fromid
		self.to_node = toid

	def typestring(self):
		return 'AssociationRepresenter'

	def resolveIds(self, ctx):
		self.from_node = ctx.get_class_by_id(self.from_node).classname
		self.to_node = ctx.get_class_by_id(self.to_node).classname

	def store(self, context, target):
		location = context.location + '.' + self.name

		values = self.buildDict(context.mvk, target, location, self.body)
		rl = context.mvk.read(LocationValue(location))
		from_port_name = str(rl.get_item().get_attribute(
							StringValue('Association.from_port')).get_value())
		#debug_print('from_port_name: ' + from_port_name)
		#debug_print('self.from_node: ' + str(self.from_node))
		values.update({
						StringValue(from_port_name)
						:
						LocationValue(self.from_node)
					})

		to_port_name = str(rl.get_item().get_attribute(
							StringValue('Association.to_port')).get_value())
		#debug_print('to_port: ' + to_port_name)
		values.update({
						StringValue(to_port_name)
						:
						LocationValue(self.to_node)
					})


		self.create(context.mvk, MappingValue({CreateConstants.TYPE_KEY: LocationValue(location),
			CreateConstants.LOCATION_KEY: LocationValue(target),
			CreateConstants.ATTRS_KEY: MappingValue(values)}))



####################################################################################

class Context(object):
	def __init__(self, location, rules, target):
		self.mvk = MvK()
		self.treemarker = []
		self.idtable = {}
		self.pivots = []
		self.asg = []
		self.location = location
		self.target = target
		self.modelname = ''
		self.modelrules = {}
		self.classrules = {}
		self.assocrules = {}

		for rulename in rules:
			if(rules[rulename]['type'] == 'Model'):
				self.modelrules.update({rulename:rules[rulename]})
			elif(rules[rulename]['type'] == 'Class'):
				self.classrules.update({rulename:rules[rulename]})
			elif(rules[rulename]['type'] == 'Association'):
				self.assocrules.update({rulename:rules[rulename]})

	def getctx(self):
		retstr = ''
		first = True
		for elem in self.treemarker:
			if first:
				retstr = elem
				first = False
			else:
				retstr += '.' + elem
		return retstr

	def addTreePath(self, item):
		self.treemarker.append(item)

	def popTreePath(self):
		self.treemarker.pop()

	def get_class_by_id(self, ident):
		return self.idtable[ident]

	def getChildElemsofType(self, elemtype, child_list):
		elems = []
		for ident in child_list:
			elem = self.get_class_by_id(ident)
			if(isinstance(elem, ClassRepresenter)):
				#debug_print('searching ' + elemtype + ' of type ' + elem.name + ' in ' + str(elem.super))
				if(elem.name == elemtype or elemtype in elem.super):
					#debug_print('matchlist: ' + elem.classname)
					elems.append(elem)
		return elems

	def betweenChildren(self, rule, child_list):
		lelems = self.getChildElemsofType(rule['source']['type'], child_list)
		if lelems == []:
			return
		#debug_print('source elems: ' + str(len(lelems)))

		relems = self.getChildElemsofType(rule['target']['type'], child_list)
		if relems == []:
			return
		#debug_print('target elems: ' + str(len(relems)))

		self.crossProduct(rule, lelems, relems)

	def processChildren(self, this_id, child_list):
		for rulename in self.assocrules:
			debug_print('running rule: ' + str(rulename))
			rule = self.assocrules[rulename]

			self.betweenChildren(rule, child_list)
			self.betweenParentsAndChildren(rule, this_id, child_list)

	def betweenParentsAndChildren(self, rule, this_id, child_list):
		lelems = self.getChildElemsofType(rule['source']['type'], [this_id])
		if lelems == []:
			return
		#debug_print('source elems: ' + str(len(lelems)))

		relems = self.getChildElemsofType(rule['target']['type'], child_list)
		if relems == []:
			return
		#debug_print('target elems: ' + str(len(relems)))

		self.crossProduct(rule, lelems, relems)

	def crossProduct(self, rule, lelems, relems):
		for elem1 in lelems:
			for elem2 in relems:
				if(elem1.id != elem2.id):
					if(self.evaluate_condition(rule,
							{'source':elem1, 'target':elem2})):
						self.applyrelation(rule,
							{'source':elem1, 'target':elem2})

	def processNonAST(self):
		for rulename in self.assocrules:
			rule = self.assocrules[rulename]
			if(rule['condition'][0] != 'equals'):
				continue

			debug_print('running rule: ' + str(rulename))
			lelems = getElemsofType(self, rule['source']['type'])
			if lelems == []:
				continue
			relems = getElemsofType(self, rule['target']['type'])
			if relems == []:
				continue

			self.crossProduct(rule, lelems, relems)

	def evaluate_condition(self, rule, elems):
		f = getattr(self, 'eval_' + rule['condition'][0], None)
		if f:
			return f(rule, elems)
		else:
			raise Exception('Internal error.')

	def getLeftRight(self, rule, elems):
		condition = rule['condition']
		leftelem = rightelem = None

		if(not str(condition[1]).startswith('@') or
			not str(condition[2]).startswith('@')):
				raise Exception('Can only be applied to identifiers with @: ' +
					str(condition[1]) + ', ' + str(condition[2]))

		if(rule['source']['name'] == condition[1][1:]):
			leftelem = elems['source']
		elif(rule['target']['name'] == condition[1][1:]):
			leftelem = elems['target']
		else:
			raise Exception('Name not found: ' + condition[1][1:])

		if(rule['source']['name'] == condition[2][1:]):
			rightelem = elems['source']
		elif(rule['target']['name'] == condition[2][1:]):
			rightelem = elems['target']
		else:
			raise Exception('Name not found: ' + condition[2][1:])

		debug_print('left: ' + str(leftelem.id) + ' right: ' + str(rightelem.id))

		return { 'left': leftelem, 'right': rightelem }

	def eval_first(self, rule, elems):
		debug_print('condition: ' + str(rule['condition']))
		debug_print('elems: ' + str(elems))

		leftright = self.getLeftRight(rule, elems)

		left = self.get_class_by_id(leftright['left'].id)
		debug_print('completelist: ' + str(left.children))

		searchid = left.getNthOfType(self, 0, rule['target']['type'])
		#debug_print('searched for: ' + rule['target']['type'] + ' and found: ' + str(searchid))

		return searchid == leftright['right'].id

	def eval_second(self, rule, elems):
		#debug_print('condition: ' + str(rule['condition']))
		#debug_print('elems: ' + str(elems))

		leftright = self.getLeftRight(rule, elems)

		left = self.get_class_by_id(leftright['left'].id)
		#debug_print('completelist: ' + str(left.children))

		searchid = left.getNthOfType(self, 1, rule['target']['type'])
		debug_print('searched for: ' + rule['target']['type'] + ' and found: ' + str(searchid))
		return searchid == leftright['right'].id

	def eval_nextTo(self, rule, elems):
		#debug_print('condition: ' + str(rule['condition']))
		#debug_print('elems: ' + str(elems))

		leftright = self.getLeftRight(rule, elems)
		leftparent = self.get_class_by_id(leftright['left'].parent)
		rightparent = self.get_class_by_id(leftright['right'].parent)
		if(leftparent != rightparent):
			return False

		leftindex = leftparent.getIndexOfChildIdWithType(
						self, leftright['left'].id, rule['source']['type'])

		#debug_print('searched for: ' + rule['source']['type'] + ' on id ' +
					#str(leftright['left'].id) + ' and found: ' + str(leftindex))

		leftindex += 1

		rightindex = leftparent.getIndexOfChildIdWithType(
						self, leftright['right'].id, rule['target']['type'])

		#debug_print('searched for: ' + rule['target']['type'] + ' on id ' +
					#str(leftright['right'].id) + ' and found: ' + str(rightindex))

		#debug_print('completelist: ' + str(leftparent.children))

		return rightindex == leftindex

	def eval_direct(self, rule, elems):
		leftright = self.getLeftRight(rule, elems)

		return leftright['right'].id in leftright['left'].children

	def eval_equals(self, rule, elems):
		left = right = ''
		condition = rule['condition']
		leftvalue = condition[1]
		left = self.eval_atom(rule, elems, leftvalue)

		rightvalue = condition[2]
		right = self.eval_atom(rule, elems, rightvalue)

		return left == right

	def eval_atom(self, rule, elems, value):

		if(value.startswith('@')):
			expr = re.compile('\w+').findall(value[1:])
			varname = expr[0]
			elem = None
			if(rule['source']['name'] == varname):
				elem = elems['source']
			elif(rule['target']['name'] == varname):
				elem = elems['target']
			else:
				raise Exception('Name not found: ' + varname)

			if(len(expr) == 1):
				#debug_print('eval_atom value 1: ' + value + ' ' + str(elem.id))
				return elem.id
			elif(len(expr) == 2):
				#debug_print('eval_atom value 2: ' + value + ' ' + str(elem.body[expr[1]]))
				return elem.body[expr[1]]
			else:
				raise Exception('Access error: ' + value[1:])
		else:
			return value

	def applyrelation(self, rule, elems):
		#debug_print('applyrelation: ' + str(elems))
		relname = rule['name']
		body = copy.deepcopy(rule['body'])

		for key in body:
			if isinstance(body[key],str):
				body.update({key:self.eval_atom(rule, elems, body[key])})
			elif isinstance(body[key],list):
				body.update({key:self.evaluate_statement(rule, elems, body[key])})

		elem = AssociationRepresenter(relname, body,elems['source'].id, elems['target'].id)
		self.asg.append(elem)

	def evaluate_statement(self, rule, elems, statement):
		f = getattr(self, 'eval_' + statement[0], None)
		if f:
			return f(rule, elems, statement)
		else:
			raise Exception('Internal error.')

	def eval_getNodeId(self, rule, elems, statement):
		return str(elems['source'].id)

	def eval_concat(self, rule, elems, statement):
		#debug_print('eval_concat')

		leftvalue = statement[1]
		rightvalue = statement[2]

		#debug_print('leftvalue ' + str(leftvalue))
		#debug_print('rightvalue ' + str(rightvalue))

		if(isinstance(leftvalue, str)):
			left = self.eval_atom(rule, elems, leftvalue)
		elif(isinstance(leftvalue,list)):
			left = self.evaluate_statement(rule, elems, leftvalue)
		else:
			Exception('Internal error: ' + leftvalue)

		if(isinstance(rightvalue, str)):
			right = self.eval_atom(rule, elems, rightvalue)
		elif(isinstance(rightvalue,list)):
			right = self.evaluate_statement(rule, elems, rightvalue)
		else:
			Exception('Internal error: ' + rightvalue)

		#debug_print('right ' + right)

		return left + right


def getElemsofType(context, elemtype):
	elems = []
	for elem in context.asg:
		if(isinstance(elem, ClassRepresenter)):
			#debug_print('searching ' + elemtype + ' of type ' + elem.name + ' in ' + str(elem.super))
			if(elem.name == elemtype or elemtype in elem.super):
				#debug_print('matchlist: ' + elem.classname)
				elems.append(elem)
	return elems

####################################################################################

class MvKLoader(object):

	def __init__(self, rules, location, path, targetlocation):
		self.idx = 0 ## tree node identifier
		self.rules = rules
		self.location = location
		self.path = path
		self.targetlocation = targetlocation

	def getNextId(self):
		self.idx += 1
		return self.idx

	def istok(self, item):
		if(isinstance(item, TokValue)):
			return True
		elif(isinstance(item, unicode)):
			return True
		return False

	def visit(self, context, tree, parent_id=0):
		#debug_print('visit with parent: ' + str(parent_id))
		this_id = -1
		child_idlist = []
		if (tree == None or self.istok(tree)):
			return {'this_id': -1, 'children': []}

		context.addTreePath(tree.head)
		if(self.activaterules(context)):
			this_id = self.getNextId()
			#debug_print(tree.head + ' activated with new id: ' + str(this_id))
		else:
			this_id = parent_id
			#debug_print(tree.head + ' not activated so id is ' + str(parent_id))

		if(not self.matchattr(context, tree)):
			for elem in tree.tail:
				visitvalue = self.visit(context, elem, this_id)
				child_id = visitvalue['this_id']
				innerlist = visitvalue['children']

				if(child_id == -1):
					continue

				#debug_print('innerchildren are: ' + str(innerlist)
				#			+ ' from element: ' + str(child_id))
				if(child_id == this_id): ## my children are your children..
					#debug_print('\t\tpassing around children.. to parent ' + str(parent_id))
					#debug_print('we still in element: ' + str(this_id))

					for elem in innerlist:
						if(not elem in child_idlist):
							child_idlist.append(elem)
				else:
					if(not child_id in child_idlist):
						child_idlist.append(child_id)
						#debug_print('we keep this: ' + str(child_id))
						#debug_print('but we lose even more... ' + str(innerlist))

		value = {'this_id': this_id, 'children': child_idlist}
		#debug_print('\t\t\tbailing out: ' + str(value))

		self.deactivaterules(context, this_id, child_idlist, parent_id)
		context.popTreePath()
		return value

	def matchattr(self, context, tree):
		for elem in context.pivots:
			for key in elem[1]['body']:
				attr = elem[1]['body'][key]
				if(not isinstance(attr,tuple)):
					continue # its already set..
				if(context.getctx().endswith('.' + attr[0])):
					#debug_print('context.getctx(): ' + context.getctx() + ' ends with elem ' + attr[0])
					#debug_print('btw the whole attr ' + str(attr))
					value = self.getAsValue(tree)
					if(value[0] == '\'' and value[len(value)-1] == '\''):
						value = value[1:-1]
					elif(value[0] == '\"' and value[len(value)-1] == '\"'):
						value = value[1:-1]

					#debug_print('prevkey ' + str(elem[1]['body'][key]))
					elem[1]['body'].update({key: value})
					#debug_print('newkey ' + str(elem[1]['body'][key]))
					return True
		return False

	def getAsValue(self, tree):
		value = ''
		for elem in tree.tail:
			if(not self.istok(elem)):
				value += self.getAsValue(elem)
			else:
				value += str(elem)
		return value

	def activaterules(self, context):
		activated = False
		for elem in self.rules: ## cycle in rules
			## only applies to model and class rules
			if(self.rules[elem]['type'] != 'Association'):
				if(context.getctx().endswith('.' + elem)):
					context.pivots.insert(0,(elem,copy.deepcopy(self.rules[elem])))
					activated = True

		return activated

	def deactivaterules(self, context, this_id, child_idlist, parent_id):
		for elem in context.pivots: ## cycle in pivots
			if(context.getctx().endswith('.' + elem[0])):
				if(elem[1]['type'] == 'Model'):
					mr = ModelRepresenter(elem[1]['name'], this_id, child_idlist, elem[1]['body'])
					context.idtable.update({this_id:mr})
					context.modelname = mr.modelname
					context.asg.append(mr)
					context.pivots.remove(elem)
					return
				elif(elem[1]['type'] == 'Class'):
					cr = ClassRepresenter(elem[1]['name'], this_id, child_idlist, parent_id, elem[1]['body'])
					context.idtable.update({this_id:cr})
					context.asg.append(cr)
					cr.fillDynamicAttributes(context)
					cr.fillSuperTypes(context)
					context.processChildren(this_id, child_idlist)
					context.pivots.remove(elem)
					return

	def load(self, path='sccd_examples/bouncing_tkinter.sccd'):
		grammarname = 'sccd_grammar.g'
		grammar = Grammar(grammars.open(os.path.join(pathname, grammarname)), auto_filter_tokens=False)
		sentence = grammar.parse(_read(path))
		debug_print(sentence.pretty())

		debug_print('loading precompiled sccd metamodel on the mvk...')
		start = time.clock()
		ctx = Context(self.location, self.rules, self.targetlocation)
		gmm = GenSCCD()
		gmm.mvk = ctx.mvk
		gmm.instance()
		tick1 = time.clock()
		debug_print('done after: %.2gs' % (tick1-start))

		debug_print('processing classes and topological relations...')
		self.visit(ctx, sentence)
		tick2 = time.clock()
		debug_print('done after: %.2gs' % (tick2-tick1))

		# get model: we assume only one model can be generated from this tree
		# virtually we could have more, but then we have to define a new notion of scope
		for elem in ctx.asg:
			if(elem.typestring() == 'ModelRepresenter'):
				elem.store(ctx, self.targetlocation)
				ctx.modelname = elem.modelname
				break

		debug_print('storing classes on the mvk...')
		for elem in ctx.asg:
			if(elem.typestring() == 'ClassRepresenter'):
				elem.store(ctx, self.targetlocation + '.' + ctx.modelname)
		tick3 = time.clock()
		debug_print('done after: %.2gs' % (tick3-tick2))

		debug_print('processing non topological relations...')
		ctx.processNonAST()
		tick4 = time.clock()
		debug_print('done after: %.2gs' % (tick4-tick3))


		debug_print('storing all relations on the mvk...')
		for elem in ctx.asg:
			if(elem.typestring() == 'AssociationRepresenter'):
				elem.resolveIds(ctx)
				elem.store(ctx, self.targetlocation + '.' + ctx.modelname)
		tick5 = time.clock()
		debug_print('done after: %.2gs' % (tick5-tick4))

		return ctx

	def debugasg(self, ctx):
		if(DEBUG is False):
			return
		for elem in ctx.asg:
			print(str(elem.id) + ', ' + str(elem.children) + ', ')
			print(str(elem.name) + ', ')
			printdic(elem.body)
		print(ctx.pivots)

###############################################################################
def printdic(dict):
	print('{')
	for elem in dict:
		print(str(elem) + ': ' + str(dict[elem]) + ', ')
	print('}')

def _read(n, *args):
	kwargs = {'encoding': 'utf-8'}
	with open(os.path.join(os.getcwd(), n), *args, **kwargs) as f:
		return f.read()

"""
if __name__ == '__main__':
	mapper = SCCD_ASG_Mapper()
	if(len(sys.argv) > 1):
		script = sys.argv[1]
		packagename = sys.argv[2]
		context = MvKLoader(mapper.rules, mapper.metamodel_location, mapper.metamodel_path, packagename).load(script)
	else: # call the default one
		context = MvKLoader(mapper.rules, mapper.metamodel_location, mapper.metamodel_path, 'MyFormalisms').load()
	shell = Shell()
	shell.mvk = context.mvk
	shell.setupCommandLine()
"""