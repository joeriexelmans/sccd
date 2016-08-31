.. SCCD documentation master file, created by
   sphinx-quickstart on Tue Aug 16 10:17:10 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SCCD Documentation
==================

SCCD [SCCD]_ is a language that combines the Statecharts [Statecharts]_ language with Class Diagrams. It allows users to model complex, timed, autonomous, reactive, dynamic-structure systems.

The concrete syntax of SCCD is an XML-format loosely based on the `W3C SCXML recommendation <https://www.w3.org/TR/scxml/>`_. A conforming model can be compiled to a number of programming languages, as well as a number of runtime platforms implemented in those languages. This maximizes the number of applications that can be modelled using SCCD, such as user interfaces, the artificial intelligence of game characters, controller software, and much more.

This documentation serves as an introduction to the SCCD language, its compiler, and the different supported runtime platforms.

Contents
--------

.. toctree::
   :maxdepth: 2

    Installation <installation>
    Language Features <language_features>
    Compiler <compiler>
    Runtime Platforms <runtime_platforms>
    Examples <examples>
    Semantic Options <semantic_options>
    Socket Communication <sockets>
    Internal Documentation <internal_documentation>
    
References
----------
    
.. [SCCD] Simon Van Mierlo, Yentl Van Tendeloo, Bart Meyers, Joeri Exelmans, and Hans Vangheluwe. SCCD: SCXML extended with class diagrams. In *3rd Workshop on Engineering Interactive Systems with SCXML, part of EICS 2016*, 2016. [`LINK <http://www.scxmlworkshop.de/eics2016/submissions/SCCD%20SCXML%20Extended%20with%20Class%20Diagrams.pdf>`_]
.. [Statecharts] David Harel. Statecharts: A visual formalism for complex systems. *Sci. Comput. Program. 8*, 3 (1987), 231–274. [`LINK <http://www.inf.ed.ac.uk/teaching/courses/seoc/2005_2006/resources/statecharts.pdf>`_]
