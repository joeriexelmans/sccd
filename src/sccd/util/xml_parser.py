from enum import *
from typing import *
from lxml import etree
import termcolor
from sccd.util.debug import *

class XmlError(Exception):
  pass

class XmlErrorElement(Exception):
  def __init__(self, el: etree.Element, msg):
    super().__init__(msg)
    self.el = el

# Returns multiline string containing fragment of src_file with 'el' XML element highlighted.
def xml_fragment(src_file: str, el: etree.Element) -> str:
    # This is really dirty, but can't find a clean way to do this with lxml.

    parent = el.getparent()
    if parent is None:
      parent = el

    with open(src_file, 'r') as file:
      lines = file.read().split('\n')
      numbered_lines = list(enumerate(lines, 1))

    parent_lines = etree.tostring(parent).decode('utf-8').strip().split('\n')
    el_lines = etree.tostring(el).decode('utf-8').strip().split('\n')
    text = []

    parent_firstline = parent.sourceline
    parent_lastline = parent.sourceline + len(parent_lines) - 1

    el_firstline = el.sourceline
    el_lastline = el.sourceline + len(el_lines) - 1

    from_line = max(parent_firstline, el_firstline - 4)
    to_line = min(parent_lastline, el_lastline + 4)

    def f(tup):
      return from_line <= tup[0] <= to_line

    for linenumber, line in filter(f, numbered_lines):
      ll = "%4d: %s" % (linenumber, line)
      if el_firstline <= linenumber <= el_lastline:
        ll = termcolor.colored(ll, 'yellow')
      text.append(ll)

    return "\n\n%s\n\n%s:\nline %d: <%s>: " % ('\n'.join(text), src_file,el.sourceline, el.tag)

    
ParseElementF = Callable[[etree.Element], Optional['RulesWDone']]
OrderedElements = List[Tuple[str, ParseElementF]]
UnorderedElements = Dict[str, ParseElementF]
Rules = Union[OrderedElements, UnorderedElements]
RulesWDone = Union[Rules, Tuple[Rules,Callable]]

# A very beefy parsing function on top of 'lxml' event-driven parsing, that takes parsing rules in a very powerful, schema-like format.
# The 'rules' passed should be one of:
#    1) A dictionary of XML tags mapped to a visit-calback, to denote that any of the tags in are allowed in any order and in any multiplicity.
#    2) A list of tuples (pairs): (tag, visit-callback), to denote that the tags MUST occur in the given order. Additionally, each tag may have a multiplicity-suffix: '*' for any, '+' for at least once, '?' for optional, and no suffix for once.
# A visit callback will be called with a single 'etree.XMLElement' argument, when an opening tag of an XML element is encountered and matches with a rule in the current 'rules' object.
# Every visit callback MAY return a new set of 'rules' (= a dict or list) that will be used for the children elements of the element visited. If nothing is returned, the element is not allowed to have any children.
# Finally, a 'rules' object may also be a tuple (rules, when_done), where 'rules' is a dict or list as described above, and 'when_done' is an additional callback, called when the closing tag of the element is encountered (after all children have been visited). From this callback, any value may be returned. The values returned by the 'when_done'-callbacks of the children of an element will be passed as arguments to the 'when_done' of this element.
# The parse function itself returns the value returned by the parser rule of the 'when_done' of the document's root element.
def parse(src_file, rules: RulesWDone, ignore_unmatched = False, decorate_exceptions = ()):

  class Multiplicity(Flag):
    AT_LEAST_ONCE = auto()
    AT_MOST_ONCE = auto()

    ANY = 0
    ONCE = AT_LEAST_ONCE | AT_MOST_ONCE
    OPTIONAL = AT_MOST_ONCE
    MULTIPLE = AT_LEAST_ONCE

    @staticmethod
    def parse_suffix(tag: str) -> Tuple[str, 'Multiplicity']:
      if tag.endswith("*"):
        m = Multiplicity.ANY
        tag = tag[:-1]
      elif tag.endswith("?"):
        m = Multiplicity.OPTIONAL
        tag = tag[:-1]
      elif tag.endswith("+"):
        m = Multiplicity.MULTIPLE
        tag = tag[:-1]
      else:
        m = Multiplicity.ONCE
      return tag, m

    def unparse_suffix(self, tag: str) -> str:
      return tag + {
        Multiplicity.ANY: "*",
        Multiplicity.ONCE: "",
        Multiplicity.OPTIONAL: "?",
        Multiplicity.MULTIPLE: "+"
      }[self]

  rules_stack = [rules]
  results_stack = [[]]

  for event, el in etree.iterparse(src_file, events=("start", "end")):
    try:
      when_done = None
      pair = rules_stack[-1]
      if isinstance(pair, tuple):
        rules, when_done = pair
      else:
        rules = pair
      if event == "start":
        # print("start", el.tag)

        parse_function = None
        if isinstance(rules, dict):
          # print("rules:", list(rules.keys()))
          try:
            parse_function = rules[el.tag]
          except KeyError as e:
            pass

        elif isinstance(rules, list):
          # print("rules:", [rule[0] for rule in rules])
          # Expecting elements in certain order and with certain multiplicities
          while len(rules) > 0:
            tag_w_suffix, func = rules[0]
            tag, m = Multiplicity.parse_suffix(tag_w_suffix)
            if tag == el.tag:
              if m & Multiplicity.AT_MOST_ONCE:
                # We don't allow this element next time
                rules = rules[1:]
                rules_stack[-1] = (rules, when_done)

              elif m & Multiplicity.AT_LEAST_ONCE:
                # We don't require this element next time
                m &= ~Multiplicity.AT_LEAST_ONCE
                rules = list(rules) # copy list before editing
                rules[0] = (m.unparse_suffix(tag), func) # edit rule
                rules_stack[-1] = (rules, when_done)

              parse_function = func
              break
            else:
              if m & Multiplicity.AT_LEAST_ONCE:
                raise XmlError("Expected required element <%s>" % tag)
              else:
                # Element is skipable
                rules = rules[1:]
                rules_stack[-1] = (rules, when_done)
        else:
          print(rules)
          assert False # rule should always be a dict or list

        if parse_function:
          children_rules = parse_function(el)
          if children_rules:
            rules_stack.append(children_rules)
          else:
            rules_stack.append([])
        else:
          if not ignore_unmatched:
            raise XmlError("Unexpected element.")
          else:
            rules_stack.append([])
        results_stack.append([])

      elif event == "end":
        if isinstance(rules, list) and len(rules) > 1:
          for rule in rules:
            tag_w_suffix, func = rule
            tag, m = Multiplicity.parse_suffix(tag_w_suffix)
            if m & Multiplicity.AT_LEAST_ONCE:
              raise XmlError("Expected required element <%s> " % tag)
        children_results = results_stack.pop()
        pair = rules_stack.pop()
        if isinstance(pair, tuple):
          _, when_done = pair
          if when_done:
            result = when_done(*children_results)
            # print("end", el.tag, "with result=", result)
            if result:
              results_stack[-1].append(result)
          # else:
          #   print("end", el.tag)

    except (XmlError, *decorate_exceptions) as e:
      # Assume exception occured while visiting current element 'el':
      e.args = (xml_fragment(src_file, el) + str(e),)
      raise
    except XmlErrorElement as e:
      # Element where exception occured is part of exception object:
      e.args = (xml_fragment(src_file, e.el) + str(e),)
      raise

  results = results_stack[0] # sole stack frame remaining
  if len(results) > 0:
    return results[0] # return first item, since we expect at most one item since an XML file has only one root node

def require_attribute(el, attr):
  val = el.get(attr)
  if val is None:
    raise XmlErrorElement(el, "missing required attribute '%s'" % attr)
  return val

def if_attribute(el, attr, callback):
  val = el.get(attr)
  if val is not None:
    try:
      callback(val)
    except Exception as e:
      raise XmlErrorElement(el, "attribute %s=\"%s\": %s" % (attr, val, str(e))) from e
