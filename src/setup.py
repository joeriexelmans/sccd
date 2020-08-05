from setuptools import setup, find_packages

setup(name="sccd",
      version="1.0.0",
      description="SCCD Compiler and Runtime",
      author="Simon Van Mierlo",
      author_email="Simon.VanMierlo@uantwerpen.be",
      url="http://msdl.cs.mcgill.ca/people/simonvm",
      packages=find_packages(exclude=['sccd.test']),
      include_package_data=True
)
