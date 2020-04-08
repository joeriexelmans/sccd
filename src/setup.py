from distutils.core import setup

setup(name="sccd",
      version="1.0.0",
      description="SCCD Compiler and Runtime",
      author="Simon Van Mierlo",
      author_email="Simon.VanMierlo@uantwerpen.be",
      url="http://msdl.cs.mcgill.ca/people/simonvm",
      packages=[
        'sccd',
        'sccd.action_lang',
        'sccd.action_lang.cmd',
        'sccd.action_lang.dynamic',
        'sccd.action_lang.parser',
        'sccd.action_lang.static',
        'sccd.controller',
        'sccd.model',
        'sccd.statechart',
        'sccd.statechart.cmd',
        'sccd.statechart.dynamic',
        'sccd.statechart.parser',
        'sccd.statechart.static',
        'sccd.util',
      ]
)
