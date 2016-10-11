import re

#from sccd_modelverse_sources.sccd_metamodel import Gen as GenSCCD
#from sccd_modelverse_sources.bouncing_tkinter import Gen as GenBBals

from mvk.impl.python.constants import CreateConstants, UpdateConstants
from mvk.impl.python.datatype import TypeFactory, Type, IntegerType, StringType, \
    BooleanType, FloatType
from mvk.impl.python.datavalue import MappingValue, \
    LocationValue, StringValue, FloatValue, \
    IntegerValue, BooleanValue, InfiniteValue, Iterator, AnyValue

from mvk.impl.python.object import ClabjectReference, Clabject

from mvk.mvk import MvK
import mvk
#from shell import Shell

#from sccd_to_xml_rules import XMLRules

DEBUG = False

def debug_print(_str_):
    if(DEBUG is False):
        return
    print('>>> debug: ' + _str_)


class SCCD_to_XML(object):
    def __init__(self, rules, modelverse=None):
        
        self.modelpackage = ''
        self.modelname = ''
        self.modelitem = None
        self.rules = rules
        self.outputStream = ''
        self.reset_indentation()
        
#        if(modelverse is None): # load default...
#            self.mvk = MvK()
#            gmm = GenSCCD()
#            gmm.mvk = self.mvk
#            gmm.instance()
#            gbb = GenBBals()
#            gbb.mvk = gmm.mvk
#            gbb.instance()
#        else:
        self.mvk = modelverse
        self.reservedwords = ['@newline', '@indent', '@dedent']

    def reset_indentation(self):
        self.indentation = 0
        self.lastnewline = False

    def increase_indentation(self):
        self.indentation = self.indentation + 1

    def decrease_indentation(self):
        self.indentation = self.indentation - 1

    def getidentstring(self):
        ntabs = self.indentation
        outstring = ''
        while ntabs > 0:
            outstring = outstring + '\t'
            ntabs = ntabs - 1
        return outstring

    ## override this to emmit to other outputs
    def emmitCode(self, string, tabs=False):
        string = string.replace('\[','{')
        string = string.replace('\]','}')

        if tabs is True or self.lastnewline is True:
            self.write(self.getidentstring() + string)
        else:
            self.write(string)
        self.lastnewline = False

    def newline(self):
        self.write('\n')
        self.lastnewline = True

    def write(self, string):
        self.outputStream += string

    def compile(self, location='MyFormalisms.BouncingBalls'):
        modelrule = None
        for key in self.rules:
            if(self.rules[key]['type'] == 'Model'):
                modelrule = {'key': key, 'body': self.rules[key]}

        if modelrule == None:
            raise Exception('Error: no model rule defined')

        rl = self.mvk.read(LocationValue(location))
        if(not rl.is_success()):
            raise Exception('Error: Invalid location: ' + location)

        item = rl.get_item()
        typename = str(item.typed_by().get_location())
        debug_print(typename)
        self.modelpackage = modelrule['body']['package']
        self.modelname = modelrule['body']['name']
        self.modelitem = item
        expectedtype = self.modelpackage + '.' + modelrule['body']['name']
        if(typename != expectedtype):
            raise Exception('Model at specified location is not an ' + expectedtype + ' model!')

        if(self.isEnabled(modelrule, item)):
            self.evaluateRule(modelrule, item)

    def processReserved(self, elem):
        if(elem == '@newline'):
            self.newline()
        elif(elem == '@indent'):
            self.increase_indentation()
        elif(elem == '@dedent'):
            self.decrease_indentation()

    def evaluateRule(self, rule, item):
        debug_print('evaluateRule: ' + str(rule))
        debug_print('evaluateRule: ' + str(item))
        pattern = rule['body']['pattern']
        for elem in pattern:
            if(elem.startswith('@')):
                if(elem in self.reservedwords):
                    self.processReserved(elem)
                elif(elem[1:] == '@'):
                    continue ## just ignore mute attributes
                elif(self.isAttributeIn(elem[1:], item)):
                    self.processAttributeIn(elem[1:], item)
                elif(elem[1:] in self.rules):
                    self.evaluateIn(elem[1:], item)
                else:
                    raise Exception(elem + ' not found!')
            elif(elem.startswith('\@')):
                self.emmitCode(elem[2:])
            else:
                self.emmitCode(elem)

    def evaluateRuleOnSet(self, rule, item, list):
        #debug_print('evaluateRuleOnSet: ' + str(rule))
        #debug_print('evaluateRuleOnSet: ' + str(item))
        pattern = rule['body']['pattern']
        for elem in pattern:
            if(elem.startswith('@')):
                if(elem in self.reservedwords):
                    self.processReserved(elem)
                elif(elem[1:] == '@'):
                    continue ## just ignore mute attributes
                elif(self.isAttributeIn(elem[1:], item)):
                    self.processAttributeIn(elem[1:], item)
                elif(elem[1:] in self.rules):
                    for itemlist in list:
                        self.evaluateIn(elem[1:], itemlist)
                else:
                    raise Exception(elem + ' not found!')
            elif(elem.startswith('\@')):
                self.emmitCode(elem[2:])
            else:
                self.emmitCode(elem)

    def evaluateIn(self, rulename, item):
        #debug_print('evaluateIn: ' + str(rulename))
        #debug_print('evaluateIn: ' + str(item))

        rule = {'key': rulename, 'body': self.rules[rulename]}

        if(not self.isEnabledIn(rulename, item)):
            return

        if(rule['body']['type'] == 'Class'):
            if(isinstance(item, mvk.interfaces.object.Clabject)):
                self.evaluateRule(rule, item)
            else:
                iterator = Iterator(self.modelitem.get_elements().keys())
                while(iterator.has_next()):
                    itemin = iterator.next()
                    value = self.modelitem.get_elements()[itemin]
                    #debug_print('item.get_elements()[itemin]: ' + str(value))
                    if(not isinstance(value, mvk.interfaces.object.Association)):
                        typename = str(value.typed_by().get_location())
                        if((self.modelpackage + '.' + rule['body']['name']) == typename):
                            self.evaluateRule(rule, value)
        elif(rule['body']['type'] == 'Association'):
            #debug_print('Association?')
            iterator = Iterator(item.out_associations.keys())
            alist = []
            while(iterator.has_next()):
                itemin = iterator.next()
                relvalue = item.out_associations[itemin]
                #debug_print('item.out_associations[itemin]: ' + str(relvalue))
                typename = str(relvalue.typed_by().get_location())
                #debug_print('typename: ' + typename)
                expectedtypename = self.modelpackage + '.' + rule['body']['name']
                if(expectedtypename == typename):
                    #debug_print('expectedtypename: ' + expectedtypename)
                    alist.append(relvalue.get_to_multiplicity().get_node())
            self.evaluateRuleOnSet(rule, item, alist)
        else:
            self.evaluateRule(rule, item)


    def processAttributeIn(self, elem, item):
        debug_print('processAttributeIn: ' + elem)

        reverse = False
        if(elem.startswith('-')):
            elem = elem[1:]
            reverse = True

        if(elem.startswith('(')):
            splitres = re.split('\).', elem[1:])
            if(len(splitres) == 2):
                item = self.resolveNavItem(splitres[0], reverse, item)
                debug_print('setting new item: ' + str(item))
                self.processAttributeIn(splitres[1], item)
                return
            else:
                raise Exception('Internal Syntax error on: ' + elem)

        value = item.get_attribute(StringValue(elem)).get_value()
        if(isinstance(value,AnyValue)):
            return
        self.emmitCode(str(value))

    def isEnabledIn(self, rulename, item):
        #debug_print('isEnabledIn: ' + str(rulename))
        #debug_print('isEnabledIn: ' + str(item))

        rule = {'key': rulename, 'body': self.rules[rulename]}

        if(rule['body']['type'] == 'Class'):
            #debug_print('isEnabledIn: ' + str(rule['body']['name']))

            if(isinstance(item, mvk.interfaces.object.Clabject)):
                if(self.isEnabled(rule, item)):
                    return True
            else:
                iterator = Iterator(item.get_elements().keys())
                while(iterator.has_next()):
                    itemin = iterator.next()
                    value = item.get_elements()[itemin]
                    if(not isinstance(value, mvk.interfaces.object.Association)):
                        typename = str(value.typed_by().get_location())
                        if((self.modelpackage + '.' + rule['body']['name']) == typename):
                            if(self.isEnabled(rule, value)):
                                return True
        elif(rule['body']['type'] == 'Association'):
            #debug_print('isEnabledIn: ' + str(rule['body']['target']))
            iterator = Iterator(item.out_associations.keys())
            while(iterator.has_next()):
                itemin = iterator.next()
                relvalue = item.out_associations[itemin]
                typename = str(relvalue.typed_by().get_location())
                #debug_print('typename: ' + typename)
                expectedtypename = self.modelpackage + '.' + rule['body']['name']
                #debug_print('expectedtypename: ' + expectedtypename)
                if(expectedtypename == typename):
                    if(self.isEnabled(rule, relvalue.get_to_multiplicity().get_node())):
                        return True
        elif(rule['body']['type'] == 'Attribute'):
            return self.isEnabled(rule, item)

        return False

    def hasExpectedType(self, expectedtype, elem):
        item = elem.typed_by()
        lastname = re.compile('\w+').findall(str(item.get_location())).pop()
        if(self.modelname + '.' + lastname == expectedtype):
            return True

        iterator = Iterator(item.get_all_super_classes())
        while(iterator.has_next()):
            itemin = iterator.next()
            lastname = re.compile('\w+').findall(str(itemin.get_location())).pop()
            if(self.modelname + '.' + lastname == expectedtype):
                return True

        return False

    def isEnabled(self, rule, item):
        debug_print('isEnabled rule: ' + str(rule))
        debug_print('isEnabled item: ' + str(item.typed_by().get_location()))

        if(rule['body']['type'] == 'Class'):
            if(not self.hasExpectedType(rule['body']['name'], item)):
                return False

        pattern = rule['body']['pattern']
        nonterminalFound = False
        for elem in pattern:
            if(elem.startswith('@')):
                if(elem in self.reservedwords):
                    continue
                if(elem[1:] == '@'):
                    return True
                elif(self.isAttributeIn(elem[1:], item)):
                    nonterminalFound = True
                    if(self.hasValue(elem[1:], item)):
                        return True
                elif(elem[1:] in self.rules):
                    nonterminalFound = True
                    if(self.isEnabledIn(elem[1:], item)):
                        return True
            else:
                continue

        return not nonterminalFound

    def resolveNavItem(self, navexpr, reverse, item):
        debug_print('resolveNavItem: ' + navexpr)
        if(isinstance(item, mvk.interfaces.object.Association)):
            return item
        if(isinstance(item, mvk.interfaces.object.Clabject)):
            if(reverse):
                iterator = Iterator(item.get_in_associations())
            else:
                iterator = Iterator(item.get_out_associations())

            debug_print('here!!!!')

            while(iterator.has_next()):
                association = iterator.next()
                name = str(association.get_name())
                typename = str(association.typed_by().get_location())
                debug_print('name: ' + name)
                debug_print('typename: ' + typename)
                if(typename.endswith(navexpr)):
                    if(reverse):
                        return association.get_from_multiplicity().get_node()
                    else:
                        return association.get_to_multiplicity().get_node()
        raise Exception('Type not found: ' + navexpr)

    def isAttributeIn(self, elem, item):
        debug_print('isAttributeIn: ' + elem)
        debug_print('isAttributeIn item: ' + str(item))

        reverse = False
        if(elem.startswith('-')):
            elem = elem[1:]
            reverse = True

        if(elem.startswith('(')):
            splitres = re.split('\).', elem[1:])
            if(len(splitres) == 2):
                item = self.resolveNavItem(splitres[0], reverse, item)
                debug_print('setting new item: ' + str(item))
                isattribute = self.isAttributeIn(splitres[1], item)
                debug_print('was found? ' + str(isattribute))
                return isattribute
            else:
                raise Exception('Internal Syntax error on: ' + elem)

        iterator  = Iterator(item.get_attributes())

        while(iterator.has_next()):
            attribute = iterator.next()
            name = str(attribute.get_name())
            if(elem == name):
                return True

    def hasValue(self, elem, item):
        debug_print('hasValue: ' + elem + ' in ' + str(item))

        reverse = False
        if(elem.startswith('-')):
            elem = elem[1:]
            reverse = True

        if(elem.startswith('(')):
            splitres = re.split('\).', elem[1:])
            if(len(splitres) == 2):
                item = self.resolveNavItem(splitres[0], reverse, item)
                debug_print('setting new item: ' + str(item))
                hasValue = self.hasValue(splitres[1], item)
                debug_print('has value? ' + str(hasValue))
                return hasValue
            else:
                raise Exception('Internal Syntax error on: ' + elem)


        value = item.get_attribute(StringValue(elem)).get_value()
        if(isinstance(value,AnyValue)):
            return False
        #debug_print('has indeed a value! on: ' + elem + str(value))
        return True

    def outputTo(self, output='console'):
        if(output == 'console'):
            print(self.outputStream)
        else:
            fo = open(output, 'a')
            fo.write(self.outputStream)
            fo.close()

if __name__ == '__main__':
    pass
    #compiler = SCCD_to_XML(XMLRules().rules)

    #compiler.compile()
    #compiler.outputTo()

    #shell = Shell()
    #shell.mvk = compiler.mvk
    #shell.setupCommandLine()

