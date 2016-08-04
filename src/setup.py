from distutils.core import setup

setup(name="sccd",
      version="1.0.0",
      description="SCCD Compiler and Runtime",
      author="Simon Van Mierlo",
      author_email="Simon.VanMierlo@uantwerpen.be",
      url="http://msdl.cs.mcgill.ca/people/simonvm",
      packages=['sccd', 'sccd.runtime', 'sccd.runtime.libs', 'sccd.compiler'],
      package_dir={'sccd': 'python_sccd', 'sccd.runtime': 'python_sccd/python_sccd_runtime', 'sccd.runtime.libs': 'python_sccd/python_sccd_runtime/libs', 'sccd.compiler': 'python_sccd/python_sccd_compiler'}
)
