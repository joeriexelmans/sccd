Language Features
=================
SCCD(XML)'s notation is loosely based on the `W3C SCXML recommendation <https://www.w3.org/TR/scxml/>`_. It adds concepts of Class Diagrams. In essence, an SCCD model consists of a number of classes that are related to each other through associations. Each class has a Statechart, defining its runtime behavior.

One class is the default class. When the system is run, the runtime creates and starts one instance of that class. Instances can create, start, and delete instances of classes (if it's allowed by the constraints modelled on the class diagram). They can also create and delete instances of associations (*i.e.* links between instances). These links are used for one instance to communicate with (an)other instance(s).

Top-Level Elements
------------------

.. _diagram:

<diagram>
^^^^^^^^^
The top-level element of an SCCD model is a ``<diagram>``. It has two attributes:

* *name* specifies the name of the diagram. For models compiled to Python, this is purely informative, while in Javascript this is the name of the namespace to which the compiled classes belong.
* *author* specifies who authored the model

Children:

* ``[0..1]`` :ref:`description`
* ``[0..1]`` :ref:`top`
* ``[0..n]`` :ref:`inport_outport`
* ``[1..n]`` :ref:`class`

.. _description:

<description>
^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`diagram`.

The ``<description>`` element contains a description of the diagram and optionally occurs once. It will be placed as a comment at the top of the compiled file.

.. _top:

<top>
^^^^^
.. note:: This is a child element of :ref:`diagram`.
.. warning:: Python only!

The ``<top>`` element can be used to import additional library modules to be used by the classes modelled in the diagram. It can optionally occur once.

.. _inport_outport:

<inport> and <outport>
^^^^^^^^^^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`diagram` or :ref:`class`.

An ``<inport>`` models a communication channel which can receive events from the outside world. An ``<outport>`` models a communication channel with which instances can send event to the outside world.

Ports have one attribute: a *name*. This name can be referenced either in :ref:`transition` (for input ports) or :ref:`raise` (for output ports).

In case the port is a child of a class, the port is local to that class. Each instance of the class will receive a private instance of the port, on which only they can receive events or can send events to.

Class Diagram Concepts
----------------------

.. _class:

<class>
^^^^^^^
Classes are the basic building block of an SCCD diagram. They model structure in the form of attributes and relations with other classes, and behavior in the form of methods (which can change the value of attributes) and a Statecharts model (which governs the runtime behavior of the class).

A ``<class>`` element has three attributes:

* *name*: the name of the class
* *default*: true if this is the default class (of which one instance is created and started at the start of executing the compiled code)
* *src*: the location of a separate XML file (relative to the location in which the main diagram is compiled), containing the definition of the class. If this attribute is set, the *name* attribute cannot be set, nor can the class element have any children.

Children:

* ``[0..1]`` :ref:`relationships`
* ``[0..n]`` :ref:`attribute`
* ``[0..1]`` :ref:`constructor`
* ``[0..1]`` :ref:`destructor`
* ``[0..n]`` :ref:`method`

.. _relationships:

<relationships>
^^^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`class`.

Models a number of relationships between its parent class and other classes of the diagram.

Children:

* ``[0..n]`` :ref:`association`
* ``[0..n]`` :ref:`inheritance`

.. _association:

<association>
^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`relationships`.

An association relation can be insantiated in order to link two instances at runtime, and those instances to exchange messages over that link. An association has two attributes:

* *name*: the name of the association
* *class*: the name of the target class
* *min*: the minimal cardinality of the association (defaults to 0)
* *max*: the maximum cardinality of the association (defaults to infinity)

.. _inheritance:

<inheritance>
^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`relationships`.

An inhertiance relation allows one class to inherit all methods and attribute from another class. Behaviour (*i.e.*, the :ref:`scxml` element) of the parent is not inherited. An inheritance relation has four attributes:

* *class*: the name of the target class
* *priority*: allows to specify in which order classes need to be inherited (in case of multiple inheritance). Inheritance relations with higher priority are inherited from first.

.. _attribute:

<attribute>
^^^^^^^^^^^
.. note:: This is a child element of :ref:`class`.

An :ref:`attribute` element has two attributes:

* *name*: the name of the attribute
* *type*: the type of the attribute

.. _constructor:

<constructor>
^^^^^^^^^^^^^
.. note:: This is a child element of :ref:`class`.

The constructor is called when an object is instantiated. It is used to initialize the instance's attribute values.

Children:

* ``[0..n]`` :ref:`parameter`
* ``[1..1]`` :ref:`body`

.. _destructor:

<destructor>
^^^^^^^^^^^^
.. note:: This is a child element of :ref:`class`.

The destructor is called just before an object is deleted.

Children:

* ``[1..1]`` :ref:`body`

.. _method:

<method>
^^^^^^^^
.. note:: This is a child element of :ref:`class`.

A method is a block of action code that can be called repeatedly in other code blocks that belong to the same class definition. It has two attributes:

* *name*: the name of the method
* *type*: the type of the return value (optional)

Children:

* ``[0..n]`` :ref:`parameter`
* ``[1..1]`` :ref:`body` 

.. _body:

<body>
^^^^^^
.. note:: This is a child element of :ref:`method`, :ref:`constructor`, or :ref:`destructor`.

A :ref:`body` element is a block of action code in a programming language (depending on the target language to which the model is compiled). It allows to call other functions and change the values of instance variables. If any parameters were defined as children of this element's parent, they can be referenced by name.

Statechart Concepts
-------------------

.. _scxml:

<scxml>
^^^^^^^
.. note:: This is a child element of :ref:`class`.

The top-level element containing the Statecharts definition of its parent class. It has one attribute:

* *initial*: specifies the initial child state of the Statechart (optional). If omitted, the first child in document order is the initial state.
* *big_step_maximality*: (optional). See :ref:`big_step_maximality`. Allowed values are "take_many" (default), "take_one".
* *internal_event_lifeline*: (optional). See :ref:`internal_event_lifeline`. Allowed values are "queue" (default), "next_small_step", "next_combo_step".
* *input_event_lifeline*: (optional). See :ref:`input_event_lifeline`. Allowed values are "first_combo_step" (default), "first_small_step", "whole".
* *priority*: (optional). See :ref:`priority`. Allowed values are "source_parent" (default), "source_child".
* *concurrency*: (optional). See :ref:`concurrency`. Allowed values are "single" (default), "many".

Children:

* ``[0..n]`` :ref:`state`.
* ``[0..n]`` :ref:`parallel`.

.. _state:

<state>
^^^^^^^
.. note:: This is a child element of :ref:`scxml`, :ref:`state`, or :ref:`parallel`.

A state is the basic building block of a Statechart. It represents a "mode" the system can be in. A state can be entered (which executes an optional block of executable content) and exited (which executes an optional block of executable content) using transitions (which execute an optional block of executable content). States can be hierarchical (*i.e.*, one state can contain other states). A state has two attributes:

* *id*: the identifier of the state. Needs to be unique with respect to other state ids on the same level (*i.e.*, the parent state cannot have two children with identical ids).
* *initial*: Specifies the initial child state, if this state is a composite state (optional). If omitted, the first child in document order is the initial state.

Children:

* ``[0..n]`` :ref:`transition`.
* ``[0..n]`` :ref:`state`.
* ``[0..n]`` :ref:`parallel`.
* ``[0..n]`` :ref:`history`.
* ``[0..1]`` :ref:`onentry`.
* ``[0..1]`` :ref:`onexit`.

.. _parallel:

<parallel>
^^^^^^^^^^
.. note:: This is a child element of :ref:`scxml`, :ref:`state`, or :ref:`parallel`.

A parallel state's children run, as the name reveals, in parallel. This means that each child of the parallel state is able to execute a transition *at the same time*. This is useful to naturally model concurrent behavior, such as animating elements on a canvas while also listening for user input. A paralle state has one attribute:

* *id*: the identifier of the parallel state. Needs to be unique with respect to other state ids on the same level (*i.e.*, the parent state cannot have two children with identical ids).

Children:

* ``[0..n]`` :ref:`transition`.
* ``[0..n]`` :ref:`state`. These children **must** be composite.
* ``[0..n]`` :ref:`parallel`.
* ``[0..n]`` :ref:`history`.
* ``[0..1]`` :ref:`onentry`.
* ``[0..1]`` :ref:`onexit`.

.. warning:: A transition from a child state cannot exit the parallel region, as this breaks encapsulation and can interfere with the behavior of other children of the parallel state. Only transitions directly from the parallel state can exit the parallel region (which will automatically exit its children as well).

.. _transition:

<transition>
^^^^^^^^^^^^
.. note:: This is a child element of :ref:`scxml`, :ref:`state`, or :ref:`parallel`.

A transition allows the system to change state (*i.e.*, go from one "mode" to the next). Transitions are *triggered* by an event or a timeout, or can be spontaneous. They can optionally specify a condition that additionally needs to evaluate to true. A transition can have five attributes:

* *target*: the target state of the transition. See :ref:`state_referencing` for more details.
* *after*: (optional) an amount of seconds that need to pass before this transition is triggered. Cannot occur together with *event*. Note that the timer starts counting when the parent state is entered. The timer is cancelled when the state is exited.
* *event*: (optional) the name of the event that triggers this transitions. Cannot occur together with *after*.
* *port*: (optional) specifies the name of the port on which the event that triggers this transition will arrive. Needs to occur together with *event*, and cannot occur together with *after*.
* *cond*: (optional) a condition that evaluates to a boolean value. Can make use of instance variables, and names of parameters passed to the transition.

Children:

* ``[0..n]`` :ref:`parameter`
* ``[0..n]`` :ref:`raise`
* ``[0..n]`` :ref:`script`
* ``[0..n]`` :ref:`log`

The semantics of executing a transition are as follows:

#. The exit set consists of the active descendants of the least-common ancestor state of the transition's source and target state. All states in the exit set are exited in order ("youngest" child first), executing their exit actions.
#. All executable content of the transition is executed in document order.
#. The enter set consists of the transition's target state, its children, and its ancestors that are not an ancestor of the source state. They are entered in order ("oldest" state first), executing their enter actions.

.. _history:

<history>
^^^^^^^^^
.. note:: This is a child element of :ref:`state`, or :ref:`parallel`.

A history state keeps track of the current configuration when its parent state is exited. If a transition has the history state as a target, the configuration that was saved is restored. If no configuration was saved yet, the default state is entered instead. A history state has two attributes:

* *id*: the identifier of the state. Needs to be unique with respect to other state ids on the same level (*i.e.*, the parent state cannot have two children with identical ids).
* *type*: (optional) either "shallow" (default) or "deep". A shallow history state only saves the active states on its level (not the active children of those states). A deep history state saves the active states on its level, and all active states on lower levels.

A history state cannot have children.

.. _onentry:

<onentry>
^^^^^^^^^
.. note:: This is a child element of :ref:`state`, or :ref:`parallel`.

An entry action is executed when a state is entered. Executable content is executed in document order.

Children:

* ``[0..n]`` :ref:`raise`
* ``[0..n]`` :ref:`script`
* ``[0..n]`` :ref:`log`

.. _onexit:

<onexit>
^^^^^^^^^
.. note:: This is a child element of :ref:`state`, or :ref:`parallel`.

An exit action is executed when a state is exited. Executable content is executed in document order.

Children:

* ``[0..n]`` :ref:`raise`
* ``[0..n]`` :ref:`script`
* ``[0..n]`` :ref:`log`

.. _state_referencing:

State Referencing
^^^^^^^^^^^^^^^^^

States need to be referenced when they are the target of a :ref:`transition` or appear in INSTATE :ref:`macros`. SCCD identifies states hierarchically and evaluates state references in the context of the state where the state reference occurs.

* ``.`` is the state itself
* ``<empty string>`` is the root (*i.e.*, the :ref:`scxml` element)
* ``..`` goes up one level (to the parent state)
* ``a`` is the child with id 'a'
* ``a/b`` with *a* and *b* arbitrary state expressions evaluates state expression *b* in the context of the state found with state expression *a*.

Examples:

* ``../A`` will look for a state with id 'A' in the parent state
* ``/A`` will look for a state with id 'A' in the root
* ``A/B`` will look for a state with id 'B' in child with id 'A'


Executable Content
------------------

Actions are executed when a :ref:`transition` is executed. There are three types of actions: event raises (which can in turn trigger other transitions), scripts (which can call functions and update instance variables) and log statements.

.. _raise:

<raise>
^^^^^^^
.. note:: This is a child element of :ref:`transition`, :ref:`onentry`, or ref:`onexit`.

Raising an event allows to notify the outside world, the Statechart, or another instance. An event has a name, and optionally parameter values that are sent along with the event. As a result, a :ref:`transition` can be triggered elsewhere in the Statechart or in the receiving instance.

A ref:`raise` element can have three attributes: *scope*, *port*, and *target*. They are used to explicitly define the scope of the raised event. Either the event is local to the Statechart, it is broadcast to all instances in the diagram, it is narrowcast to a specific instance, to the :ref:`object_manager`, or to an output port.

The table bellow summarizes how the different scopes are specified.

.. rst-class:: table-with-borders

+-------------+-------+-----------+-------------+-----------------+-------------+
| attr/scope  | local | broadcast | narrowcast  | object manager  | output      |
+=============+=======+===========+=============+=================+=============+
| *scope*     |\-\-\- | "broad"   | "narrow"    | "cd"            | "output"    |
+-------------+-------+-----------+-------------+-----------------+-------------+
| *port*      |\-\-\- |\-\-\-\-\- |\-\-\-\-\-\- |\-\-\-\-\-\-\-\- | port_name   |
+-------------+-------+-----------+-------------+-----------------+-------------+
| *target*    |\-\-\- |\-\-\-\-\- | link_name   |\-\-\-\-\-\-\-\- |\-\-\-\-\-\- |
+-------------+-------+-----------+-------------+-----------------+-------------+

A "link name" identifies a specific (set of) connected instance(s) of the instance that raised the event. For example, if class "A" and "B" are connected via an association "A_to_B", valid values for "link_name could be:

* "'A_to_B'" to send to all instances of B with which the instance of A that raises the event is connected
* "'A_to_B[idx]'" where *idx* is a valid link index, which is sent by the :ref:`object_manager` as a reply to a *create_instance* request.
* "self.the_link_name" if this evaluates to a legal link name.

.. _script:

<script>
^^^^^^^^
.. note:: This is a child element of :ref:`transition`, :ref:`onentry`, or ref:`onexit`.

A :ref:`script` element is similar to a :ref:`body` element: a block of action code in a programming language (depending on the target language to which the model is compiled). It allows to call other functions and change the values of instance variables. If any parameters were defined as children of this element's parent (in the case of a :ref:`transition`), they can be referenced by name.

.. _log:

<log>
^^^^^
.. note:: This is a child element of :ref:`transition`, :ref:`onentry`, or ref:`onexit`.

Allows to log a string.

.. _parameter:

<parameter>
^^^^^^^^^^^
.. note:: This is a child element of :ref:`transition`, :ref:`raise`, :ref:`method`, or :ref:`constructor`.

Depending on where the :ref:`parameter` element is placed, it is either a formal parameter, or an actual parameter value.

In the case it is a child of a :ref:`transition`, :ref:`method`, or :ref:`constructor`, it is a formal parameter. It then has three attributes:

* *name*: the name of the parameter
* *type*: (optional) the type of the parameter
* *default*: (optional) the default value of the parameter

.. note:: Parameters are positional.

In the case it is a child of a :ref:`raise`, it is an actual parameter value. It then has one attribute:

* *expr*: an expression that evaluates to the actual parameter value.

.. _macros:

Macros
------
Two macros are defined that can be used in the *cond* attribute of :ref:`transition` and the *expr* attribute of :ref:`parameter`:

* *INSTATE(state_reference)* returns true if the system is currently in the referenced state (see :ref:`state_referencing`).
* *SELF* returns the current object. This is useful to write platform-independent expressions. 

.. _object_manager:

Object Manager
--------------

The object manager is responsible for managing objects and links while the application is running. The instances can communicate with the object manager by raising events using the *cd* scope (see :ref:`raise`).

The object manager accepts four events:

* **create_instance**
    * Parameters:
        * *association_name*: an expression that evaluates to the name of the association that needs to be instantiated
        * *class_name*: (optional) an expression that evaluates to the name of the class to instantiate. If omitted, the target class of the association is instantiated.
        * *parameters*: (optional) the actual constructor parameter values
    * Returns Event:
        * **instance_created**\(*link_id*)
* **start_instance**
    * Parameters:
        * *link_id*: the identifier of the link with which the instance to be started is connected to the requesting instance
    * Returns Event:
        * **instance_started**\(*link_id*)
* **delete_instance**
    * Parameters:
        * *link_id*: the identifier of the link with which the instance to be deleted is connected to the requesting instance
    * Returns Event:
        * **instance_deleted**\(*link_id*)
* **associate_instance**
    * Parameters:
        * *link_expression_dst*: an expression evaluating to a set of links, of which the targets need to be associated
        * *link_expression_src*: an expression evaluating to an association, which needs to be instantiated to connect the source of the association to the targets that were evaluated in the expression above
    * Returns Event:
        * **instance_associated**\(*created_links*): the (relative) links which were created
* **disassociate_instance**
    * Parameters:
        * *link_expression_dst*: an expression evaluating to a set of links (only direct children of the current instance!), of which the targets need to be disassociated from the current instance
    * Returns Event:
        * **instance_disassociated**\(*deleted_links*): the links which were deleted