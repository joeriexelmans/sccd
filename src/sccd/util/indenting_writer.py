import sys

class IndentingWriter:

  def __init__(self, out = sys.stdout):
    self.out = out
    self.indentLevel = 0
    self.indentSpace = "    "
    self.first_write = True

  def write(self, text = ""):
    if self.first_write :
      self.first_write = False
      if text == "":
        self.out.write(self.indentLevel*self.indentSpace)
      else:
        self.out.write(self.indentLevel*self.indentSpace + text)  
    else:
      if text == "":
        self.out.write("\n" + self.indentLevel*self.indentSpace)
      else:
        self.out.write("\n" + self.indentLevel*self.indentSpace + text)
  
  def extendWrite(self, text = ""):
    self.out.write(text)
        
  def indent(self):
    self.indentLevel+=1

  def dedent(self):
    self.indentLevel-=1

  def writeCodeCorrectIndent(self, body):
    lines = body.split('\n')
    while( len(lines) > 0 and lines[-1].strip() == "") :
      del(lines[-1])
  
    index = 0;
    while( len(lines) > index and lines[index].strip() == "") :    
      index += 1
      
    if index >= len(lines) :
      return
    #first index where valid code is present
    to_strip_index = len(lines[index].rstrip()) - len(lines[index].strip()) 
    indent_type = NOT_SET;
      
    while index < len(lines):
      strip_part = lines[index][:to_strip_index]
      
      if( ('\t' in strip_part and ' ' in strip_part) or
        (indent_type == SPACES_USED and '\t' in strip_part) or
        (indent_type == TABS_USED and ' ' in strip_part)
      ) :
        raise Exception("Mixed tab and space indentation!")
      
      if indent_type == NOT_SET :
        if ' ' in strip_part :
          indent_type = SPACES_USED
        elif '\t' in strip_part :
          indent_type = TABS_USED
          
      self.write(lines[index][to_strip_index:])
      index += 1
