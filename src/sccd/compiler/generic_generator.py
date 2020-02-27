# Generic Generator by Joeri Exelmans
#
# Visits SCCD-domain constructs (see sccd_constructs.py) and converts them
# to a generic language AST (see generic_language_constructs.py), that can
# then be visited by a target language writer.

import traceback
import time

from sccd.compiler.utils import Enum, Logger
from sccd.compiler.visitor import Visitor
from sccd.compiler.sccd_constructs import FormalParameter
from sccd.compiler.stateful_writer import StatefulWriter
import sccd.compiler.generic_language_constructs as GLC

Platforms = Enum("Threads","GameLoop","EventLoop")

def compiled_class_name(class_name):
    return "Class_"+class_name

class GenericGenerator(Visitor):
    
    def __init__(self, platform):
        self.platform = platform
        self.writer = StatefulWriter()

    def generic_visit(self, node):
        Logger.showWarning("GenericGenerator has no visit method for node of type '" + str(type(node)) + "'.")

    def get(self):
        return self.writer.get()

    def visit_ClassDiagram(self, class_diagram):
        header = ("Generated by Statechart compiler by Glenn De Jonghe, Joeri Exelmans, Simon Van Mierlo, and Yentl Van Tendeloo (for the inspiration)\n")
        if class_diagram.name or class_diagram.author or class_diagram.description:
            header += "\n"
        if class_diagram.author:
            header += "Model author: " + class_diagram.author + "\n"
        if class_diagram.name:
            header += "Model name:   " + class_diagram.name + "\n"
        if class_diagram.description.strip():
            header += "Model description:\n"
            header += class_diagram.description.strip()

        self.writer.addMultiLineComment(header)
        self.writer.addVSpace()
        self.writer.addInclude(([GLC.RuntimeModuleIdentifier(), "statecharts_core"]))
        self.writer.addInclude(([GLC.RuntimeModuleIdentifier(), "event"]))
        if class_diagram.top.strip():
            self.writer.addRawCode(class_diagram.top)
        self.writer.addVSpace()

        self.writer.beginPackage(class_diagram.name)

        for c in class_diagram.classes:
            c.accept(self)

        self.writer.beginClass("Model")
        self.writer.beginConstructor()
        self.writer.beginMethodBody()
        self.writer.addAssignment(GLC.SelfProperty("inports"), GLC.ArrayExpression([GLC.String(i) for i in class_diagram.inports]))
        self.writer.addAssignment(GLC.SelfProperty("outports"), GLC.ArrayExpression([GLC.String(o) for o in class_diagram.outports]))
        self.writer.addAssignment(GLC.SelfProperty("classes"), GLC.MapExpression(
            { GLC.String(c.name) : GLC.Identifier(compiled_class_name(c.name)) for c in class_diagram.classes }))
        self.writer.addAssignment(GLC.SelfProperty("default_class"), GLC.String(class_diagram.default_class.name))
        self.writer.endMethodBody()
        self.writer.endConstructor()
        self.writer.endClass()

        # visit test node if there is one
        if class_diagram.test:
            class_diagram.test.accept(self)

        self.writer.endPackage()

    ### TESTS
    def visit_DiagramTest(self, test):
        # helper class
        self.writer.beginClass("InputEvent")
        self.writer.beginConstructor()
        self.writer.addFormalParameter("name")
        self.writer.addFormalParameter("port")
        self.writer.addFormalParameter("parameters")
        self.writer.addFormalParameter("time_offset")
        self.writer.beginMethodBody()
        self.writer.addAssignment(GLC.SelfProperty("name"), "name")
        self.writer.addAssignment(GLC.SelfProperty("port"), "port")
        self.writer.addAssignment(GLC.SelfProperty("parameters"), "parameters")
        self.writer.addAssignment(GLC.SelfProperty("time_offset"), "time_offset")
        self.writer.endMethodBody()
        self.writer.endConstructor()
        self.writer.endClass()
        self.writer.beginClass("Test")
        if test.input:
            test.input.accept(self)
        else:
            self.writer.addStaticAttribute("input_events", GLC.ArrayExpression())
        if test.expected:
            test.expected.accept(self)
        else:
            self.writer.addStaticAttribute("expected_events", GLC.ArrayExpression())
        self.writer.endClass()

    def visit_DiagramTestInput(self, test_input):
        # write array of input events
        self.writer.startRecordingExpression()
        self.writer.beginArray()
        for e in test_input.input_events:
            e.accept(self)
        self.writer.endArray()
        array_expr = self.writer.stopRecordingExpression()
        self.writer.addStaticAttribute("input_events", array_expr)

    def visit_DiagramTestInputEvent(self, event):
        self.writer.add(GLC.NewExpression("InputEvent", [GLC.String(event.name), GLC.String(event.port), GLC.ArrayExpression(event.parameters), event.time]))

    def visit_DiagramTestExpected(self, test_expected):
        # write array of slots containing expected events
        self.writer.startRecordingExpression()
        self.writer.beginArray()
        for s in test_expected.slots:
            s.accept(self)
        self.writer.endArray()
        array_expr = self.writer.stopRecordingExpression()
        self.writer.addStaticAttribute("expected_events", array_expr)

    def visit_DiagramTestExpectedSlot(self, slot):
        # write slot
        self.writer.beginArray()
        for e in slot.expected_events:
            e.accept(self)
        self.writer.endArray()

    def visit_DiagramTestEvent(self, event):
        self.writer.add(GLC.NewExpression("Event", [GLC.String(event.name), GLC.String(event.port), GLC.ArrayExpression(event.parameters)]))

    def visit_Class(self, class_node):
        if class_node.statechart:
            self.writer.beginClass("Statechart_"+class_node.name)
            class_node.statechart.accept(self)
            self.writer.endClass()

        self.writer.beginClass(compiled_class_name(class_node.name))
        self.writer.beginConstructor()
        self.writer.beginMethodBody()
        self.writer.addAssignment(GLC.SelfProperty("name"), GLC.String(class_node.name))
        if class_node.statechart:
            self.writer.addAssignment(GLC.SelfProperty("statechart"), GLC.NewExpression("Statechart_"+class_node.name, [GLC.SelfExpression()]))
        self.writer.endMethodBody()
        self.writer.endConstructor()
        self.writer.endClass()

    def visit_StateChart(self, statechart):
        # We are in the Statechart_ClassName class here:
        self.writer.beginConstructor()
        self.writer.addFormalParameter("_class")
        self.writer.beginMethodBody()

        self.writer.addAssignment(GLC.SelfProperty("_class"), GLC.Identifier("_class"))
        self.writer.addVSpace()

        self.writer.addAssignment(GLC.SelfProperty("semantics"), GLC.NewExpression("StatechartSemantics"))
        if statechart.big_step_maximality == "take_one":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "big_step_maximality"), GLC.Property("StatechartSemantics", "TakeOne"))
        elif statechart.big_step_maximality == "take_many":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "big_step_maximality"), GLC.Property("StatechartSemantics", "TakeMany"))
        if statechart.combo_step_maximality == "take_one":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "combo_step_maximality"), GLC.Property("StatechartSemantics", "ComboTakeOne"))
        elif statechart.combo_step_maximality == "take_many":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "combo_step_maximality"), GLC.Property("StatechartSemantics", "ComboTakeMany"))
        if statechart.internal_event_lifeline == "queue":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "internal_event_lifeline"), GLC.Property("StatechartSemantics", "Queue"))
        elif statechart.internal_event_lifeline == "next_small_step":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "internal_event_lifeline"), GLC.Property("StatechartSemantics", "NextSmallStep"))
        elif statechart.internal_event_lifeline == "next_combo_step":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "internal_event_lifeline"), GLC.Property("StatechartSemantics", "NextComboStep"))
        if statechart.input_event_lifeline == "first_small_step":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "input_event_lifeline"), GLC.Property("StatechartSemantics", "FirstSmallStep"))
        elif statechart.input_event_lifeline == "first_combo_step":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "input_event_lifeline"), GLC.Property("StatechartSemantics", "FirstComboStep"))
        elif statechart.input_event_lifeline == "whole":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "input_event_lifeline"), GLC.Property("StatechartSemantics", "Whole"))
        if statechart.priority == "source_parent":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "priority"), GLC.Property("StatechartSemantics", "SourceParent"))
        elif statechart.priority == "source_child":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "priority"), GLC.Property("StatechartSemantics", "SourceChild"))
        if statechart.concurrency == "single":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "concurrency"), GLC.Property("StatechartSemantics", "Single"))
        elif statechart.concurrency == "many":
            self.writer.addAssignment(GLC.Property(GLC.SelfProperty("semantics"), "concurrency"), GLC.Property("StatechartSemantics", "Many"))

        self.writer.addVSpace()

        def writeState(s, i):
            # self.writer.addComment("state %s" % ("<root>" if s.is_root else s.new_full_name))
            index_expr = GLC.MapIndexedExpression(GLC.SelfProperty("states"), GLC.String(s.new_full_name))
            clazz = "State"
            if s.is_parallel_state:
                clazz = "ParallelState"
            elif s.is_history:
                if s.is_history_deep:
                    clazz = "DeepHistoryState"
                else:
                    clazz = "ShallowHistoryState"
            self.writer.addAssignment(
                index_expr,
                GLC.NewExpression(clazz, [str(i), GLC.String(s.new_full_name), GLC.SelfExpression()])
            )
            if not s.is_root:
                if s.enter_action.action or s.has_timers:
                    self.writer.add(
                        GLC.FunctionCall(
                            GLC.Property(
                                index_expr,
                                "setEnter"
                            ),
                            [GLC.SelfProperty(s.friendly_name + "_enter")]
                        )
                    )
                if s.exit_action.action or s.has_timers:
                    self.writer.add(
                        GLC.FunctionCall(
                            GLC.Property(
                                index_expr,
                                "setExit"
                            ),
                            [GLC.SelfProperty(s.friendly_name + "_exit")]
                        )
                    )
        
        # write all states
        self.writer.addAssignment(GLC.SelfProperty("states"), GLC.MapExpression())
        for (i, s) in enumerate(statechart.states):
            writeState(s, i)

        # statechart structure
        self.writer.addVSpace()
        self.writer.addComment("structure")
        self.writer.addAssignment(GLC.SelfProperty("root"), GLC.MapIndexedExpression(GLC.SelfProperty("states"), GLC.String(statechart.root.new_full_name)))
        for (i, s) in enumerate(statechart.composites):
            for c in s.children:
                self.writer.add(
                    GLC.FunctionCall(
                        GLC.Property(
                            GLC.MapIndexedExpression(
                                GLC.SelfProperty("states"),
                                GLC.String(s.new_full_name)
                            ),
                        "addChild"),
                        [GLC.MapIndexedExpression(GLC.SelfProperty("states"), GLC.String(c.new_full_name))]
                    )
                )
                
        # fix tree at root, such that 'descendants' and 'ancestors' fields are filled in
        self.writer.add(
            GLC.FunctionCall(
                GLC.Property(
                    GLC.SelfProperty("root"),
                    "fixTree"
                )
            )
        )
        
        # defaults
        for (i, s) in enumerate(statechart.composites):
            if not s.is_parallel_state:
                self.writer.addAssignment(
                    GLC.Property(
                        GLC.MapIndexedExpression(
                            GLC.SelfProperty("states"),
                            GLC.String(s.new_full_name)
                        ),
                        "default_state"
                    ),
                    GLC.MapIndexedExpression(
                        GLC.SelfProperty("states"),
                        GLC.String(s.initial)
                    )
                )
        
        # transitions
        self.writer.addVSpace()
        self.writer.addComment("transitions")
        for s in statechart.basics + statechart.composites:
            # if s.transitions:
            #     self.writer.addVSpace()
                # self.writer.addComment("transition %s" % s.new_full_name)
            for (i, t) in enumerate(s.transitions + s.else_transitions):
                # instantiate new Transition instance
                self.writer.addAssignment(
                    GLC.LocalVariableDeclaration(
                        "%s_%i" % (s.friendly_name, i)
                    ),
                    GLC.NewExpression(
                        "Transition",
                        [
                            # GLC.SelfExpression(),
                            GLC.MapIndexedExpression(
                                GLC.SelfProperty("states"),
                                GLC.String(s.new_full_name),
                            ),
                            GLC.ArrayExpression(
                                [
                                    GLC.MapIndexedExpression(
                                        GLC.SelfProperty("states"),
                                        GLC.String(target_node.new_full_name)
                                    )
                                    for target_node in t.target.target_nodes
                                ]
                            )
                        ]
                    )
                )
                # if any action associated with transition: set executable_content to correct function (generated later)
                if t.action.sub_actions:
                    self.writer.add(
                        GLC.FunctionCall(
                            GLC.Property(
                                "%s_%i" % (s.friendly_name, i),
                                "setAction"
                            ),
                            [GLC.SelfProperty("%s_%i_exec" % (s.friendly_name, i))]
                        )
                    )
                # if any trigger associated with transition: instantiate correct Event instance
                trigger = None
                if t.trigger.is_after:
                    trigger = GLC.NewExpression("Event", [GLC.String("_after_%i" % (t.trigger.getAfterIndex()))])
                elif t.trigger.event:
                    trigger = GLC.NewExpression("Event",
                                                    [
                                                        GLC.String(t.trigger.event),
                                                        GLC.NoneExpression() if t.trigger.port is None else GLC.String(t.trigger.port)
                                                    ]
                                                )
                else:
                    trigger = GLC.NoneExpression()
                if trigger:
                    self.writer.add(
                        GLC.FunctionCall(
                            GLC.Property(
                                "%s_%i" % (s.friendly_name, i),
                                "setTrigger"
                            ),
                            [trigger]
                        )
                    )
                # if any guard associated with transition: set guard to correct function (generated later)
                if t.guard:
                    self.writer.add(
                        GLC.FunctionCall(
                            GLC.Property(
                                "%s_%i" % (s.friendly_name, i),
                                "setGuard"
                            ),
                            [GLC.SelfProperty("%s_%i_guard" % (s.friendly_name, i))]
                        )
                    )
                self.writer.add(
                    GLC.FunctionCall(
                        GLC.Property(
                            GLC.MapIndexedExpression(
                                GLC.SelfProperty("states"),
                                GLC.String(s.new_full_name)
                            ),
                            "addTransition"
                        ),
                        ["%s_%i" % (s.friendly_name, i)]
                    )
                )
        self.writer.endMethodBody()
        self.writer.endConstructor()
        
        # enter/exit actions
        for (i, s) in enumerate(statechart.composites + statechart.basics):
            if not s.is_root:
                if s.enter_action.action or s.has_timers:
                    s.enter_action.accept(self)
                if s.exit_action.action or s.has_timers:
                    s.exit_action.accept(self)
        
        # transition actions and guards
        for s in statechart.composites + statechart.basics:
            for (i, t) in enumerate(s.transitions):
                if t.action.sub_actions:
                    self.writeTransitionAction(t, i)
                if t.hasGuard():
                    self.writeTransitionGuard(t, i)


    def visit_EnterAction(self, enter_method):
        parent_node = enter_method.parent_node
        self.writer.beginMethod(parent_node.friendly_name + "_enter")
        self.writer.addFormalParameter("instance")
        self.writer.beginMethodBody()

        if enter_method.action:
            enter_method.action.accept(self)

        # take care of any AFTER events
        for transition in parent_node.transitions :
            trigger = transition.getTrigger()
            if trigger.isAfter() :
                self.writer.startRecordingExpression()
                trigger.after.accept(self)
                after = self.writer.stopRecordingExpression()
                self.writer.addComment("schedule timer")
                # self.writer.add(GLC.AssignmentExpression(GLC.Identifier("timer_event"), GLC.NewExpression("Event", [GLC.FunctionCall(GLC.Property("instance", "next_timer_id"))])))
                # self.writer.add(GLC.FunctionCall())
                self.writer.add(GLC.FunctionCall(GLC.Property(GLC.Property("instance", "_big_step"), "addOutputEvent"),
                    # function call parameter:
                    [
                        GLC.NewExpression("OutputEvent", [
                            GLC.NewExpression("Event", [GLC.String("_after_"+str(trigger.getAfterIndex()))]),
                            GLC.NewExpression("InstancesTarget", [GLC.ArrayExpression([GLC.Identifier("instance")])]),
                            after
                        ])
                    ]))
                # self.writer.add(GLC.FunctionCall(GLC.SelfProperty("addTimer"), [str(trigger.getAfterIndex()), after]))
                
        self.writer.endMethodBody()
        self.writer.endMethod()
         
    def visit_ExitAction(self, exit_method):
        parent_node = exit_method.parent_node
        self.writer.beginMethod(parent_node.friendly_name + "_exit")
        self.writer.addFormalParameter("instance")
        self.writer.beginMethodBody()
        
        # take care of any AFTER events
        for transition in parent_node.transitions:
            trigger = transition.getTrigger()
            if trigger.isAfter():
                self.writer.add(GLC.IncrementExpression(GLC.MapIndexedExpression(GLC.Property("instance", "ignore_events"), GLC.String("_after_"+str(trigger.getAfterIndex()))), GLC.Literal("1")))
                # self.writer.add(GLC.FunctionCall(GLC.SelfProperty("removeTimer"), [str(trigger.getAfterIndex())]))
                
        # execute user-defined exit action if present
        if exit_method.action:
            exit_method.action.accept(self)
        
        self.writer.endMethodBody()
        self.writer.endMethod()        

    def visit_RaiseEvent(self, raise_event):
        self.writer.startRecordingExpression()
        self.writer.begin(GLC.NewExpression("Event"))

        self.writer.addActualParameter(GLC.String(raise_event.getEventName()))
        if raise_event.isOutput():
            self.writer.addActualParameter(GLC.String(raise_event.getPort()))
        else:
            self.writer.addActualParameter(GLC.NoneExpression())

        self.writer.end()
        new_event_expr = self.writer.stopRecordingExpression()

        self.writer.startRecordingExpression()
        self.writer.beginArray()
        if raise_event.isCD():
            self.writer.add(GLC.Identifier("instance"))
        for param in raise_event.getParameters() :
            param.accept(self) # -> visit_Expression will cause expressions to be added to array
        self.writer.endArray()
        parameters_array_expr = self.writer.stopRecordingExpression()
        new_event_expr.getActualParameters().add(parameters_array_expr)

        if raise_event.isNarrow():
            self.writer.add(GLC.FunctionCall(
                GLC.Property(GLC.Property("instance", "_big_step"), "outputEventOM"), [
                    GLC.NewExpression("Event", [
                        GLC.String("narrow_cast"),
                        GLC.NoneExpression(),
                        GLC.ArrayExpression([
                            GLC.SelfExpression(),
                            raise_event.getTarget(),
                            new_event_expr])])]))
        elif raise_event.isLocal():
            self.writer.add(GLC.FunctionCall(
                GLC.Property("instance", "_raiseInternalEvent"),
                [new_event_expr]))
        elif raise_event.isOutput():
            # event to output port
            output_event = GLC.NewExpression("OutputEvent", [new_event_expr, GLC.NewExpression("OutputPortTarget", [GLC.String(raise_event.getPort())])])
            self.writer.add(GLC.FunctionCall(
                GLC.Property(GLC.Property("instance", "_big_step"), "addOutputEvent"),
                [output_event]))
        elif raise_event.isCD():
            output_event = GLC.NewExpression("OutputEvent", [new_event_expr, GLC.NewExpression("InstancesTarget", [GLC.ArrayExpression([GLC.Property("instance", "object_manager")])])])
            self.writer.add(GLC.FunctionCall(
                GLC.Property(GLC.Property("instance", "_big_step"), "addOutputEvent"),
                [output_event]))
        elif raise_event.isBroad():
            self.writer.add(GLC.FunctionCall(
                GLC.Property(GLC.Property("instance", "_big_step"), "outputEventOM"),
                [GLC.NewExpression("Event", [
                    GLC.String("broad_cast"),
                    GLC.NoneExpression(),
                    GLC.ArrayExpression([
                        GLC.SelfExpression(),
                        new_event_expr])])]))

    # ### CLASS
    # def visit_Class(self, class_node):
    #     """
    #     Generate code for Class construct
    #     """
    #     super_classes = []
    #     if not class_node.super_class_objs:
    #         # if none of the class' super classes is defined in the diagram,
    #         # we have to inherit RuntimeClassBase
    #         if class_node.statechart:
    #             # only inherit RuntimeClassBase if class has a statechart
    #             super_classes.append("RuntimeClassBase")
    #     if class_node.super_classes:
    #         for super_class in class_node.super_classes:
    #             super_classes.append(super_class)

    #     self.writer.beginClass(compiled_class_name(class_node.name), super_classes)

    #     # visit constructor
    #     class_node.constructors[0].accept(self)

    #     # visit destructor
    #     class_node.destructors[0].accept(self)
        
    #     # visit methods
    #     for i in class_node.methods:
    #         i.accept(self)

    #     # compile and initialize Statechart
    #     if class_node.statechart:
    #         class_node.statechart.accept(self)
        
    #     self.writer.endClass()
        
    ### CLASS -- CONSTRUCTOR
    def visit_Constructor(self, constructor):
        self.writer.beginConstructor()
        if constructor.parent_class.statechart:
            self.writer.addFormalParameter("controller")
        for p in constructor.getParams():
            self.writer.addFormalParameter(p.getIdent(), p.getDefault())
        self.writer.beginMethodBody() # constructor body

        if constructor.parent_class.statechart:
            self.writer.beginSuperClassConstructorCall("RuntimeClassBase")
            # self.writer.addActualParameter("controller")
            self.writer.endSuperClassConstructorCall()

            self.writer.addVSpace()
            
            for p in constructor.parent_class.inports:
                self.writer.addAssignment(
                    GLC.MapIndexedExpression(GLC.SelfProperty("inports"), GLC.String(p)),
                    GLC.FunctionCall(GLC.Property("controller", "createInputPort"), [GLC.String(p), GLC.SelfExpression()]))

            for p in constructor.parent_class.outports:
                self.writer.addAssignment(
                    GLC.MapIndexedExpression(GLC.SelfProperty("outports"), GLC.String(p)),
                    GLC.FunctionCall(GLC.Property("controller", "createOutputPort"), [GLC.String(p), GLC.SelfExpression()]))

            self.writer.addVSpace()
            self.writer.addComment("build Statechart structure")
            self.writer.add(GLC.FunctionCall(GLC.SelfProperty("build_statechart_structure"), []))

        if constructor.parent_class.attributes:
            self.writer.addVSpace()
            self.writer.addComment("user defined attributes")
            for attribute in constructor.parent_class.attributes:
                if attribute.init_value is None :
                    self.writer.addAssignment(GLC.SelfProperty(attribute.name), GLC.NoneExpression())
                else :
                    self.writer.addAssignment(GLC.SelfProperty(attribute.name), attribute.init_value)

        self.writer.addVSpace()
        self.writer.addComment("call user defined constructor")
        self.writer.beginSuperClassMethodCall(compiled_class_name( constructor.parent_class.name ), "user_defined_constructor")
        for p in constructor.getParams():
            # we can't do p.accept(self) here because 'p' is a FormalParameter
            # and we want to write it as an actual parameter
            self.writer.addActualParameter(p.getIdent())
        self.writer.endSuperClassMethodCall()
        self.writer.endMethodBody()
        self.writer.endConstructor()

        # user defined constructor
        self.writer.beginMethod("user_defined_constructor")
        for p in constructor.getParams():
            p.accept(self)
        self.writer.beginMethodBody()
        for super_class in constructor.parent_class.super_classes:
            # begin call
            if super_class in constructor.parent_class.super_class_objs:
                self.writer.beginSuperClassMethodCall(super_class, "user_defined_constructor")
            else:
                self.writer.beginSuperClassConstructorCall(super_class)
            # write actual parameters
            if super_class in constructor.super_class_parameters:
                for p in constructor.super_class_parameters[super_class]:
                    self.writer.addActualParameter(p)
            # end call
            if super_class in constructor.parent_class.super_class_objs:
                self.writer.endSuperClassMethodCall()
            else:
                self.writer.endSuperClassConstructorCall()
        self.writer.addRawCode(constructor.body)
        self.writer.endMethodBody()
        self.writer.endMethod()

    def visit_FormalParameter(self, formal_parameter):
        self.writer.addFormalParameter(formal_parameter.getIdent(), formal_parameter.getDefault())

    ### CLASS -- DESTRUCTOR
    def visit_Destructor(self, destructor):
        self.writer.beginMethod("user_defined_destructor")
        self.writer.beginMethodBody()
        if destructor.body.strip():
            self.writer.addRawCode(destructor.body)
        if destructor.parent_class.super_classes:
            self.writer.addComment("call super class destructors")
            for super_class in destructor.parent_class.super_classes:
                # begin call
                if super_class in destructor.parent_class.super_class_objs:
                    self.writer.beginSuperClassMethodCall(super_class, "user_defined_destructor")
                    self.writer.endSuperClassMethodCall()
                else:
                    self.writer.beginSuperClassDestructorCall(super_class)
                    self.writer.endSuperClassDestructorCall()
                    pass

                # self.writer.beginSuperClassMethodCall(super_class, "user_defined_destructor")
                # self.writer.endSuperClassMethodCall()
        self.writer.endMethodBody()
        self.writer.endMethod()
        
    ### CLASS -- METHOD
    def visit_Method(self, method):
        self.writer.addVSpace()
        self.writer.beginMethod(method.name, "user defined method")
        for p in method.parameters:
            p.accept(self)
        self.writer.beginMethodBody()
        self.writer.addRawCode(method.body)
        self.writer.endMethodBody()
        self.writer.endMethod()
        
    ### CLASS -- ASSOCIATION
    def visit_Association(self, association):
        self.writer.addAssignment(
            GLC.MapIndexedExpression(
                GLC.Property("instance", "associations"),
                GLC.String(association.name)),
            GLC.NewExpression("Association", [GLC.String(association.to_class), str(association.min), str(association.max)]))
        
    def visit_FormalEventParameter(self, formal_event_parameter):
        self.writer.add(formal_event_parameter.name)
        
    def writeFormalEventParameters(self, transition):
        parameters = transition.getTrigger().getParameters()
        if(len(parameters) > 0) :
            for index, parameter in enumerate(parameters):
                self.writer.startRecordingExpression()
                parameter.accept(self)
                parameter_expr = self.writer.stopRecordingExpression()
                self.writer.addAssignment(
                    GLC.LocalVariableDeclaration(parameter_expr),
                    GLC.ArrayIndexedExpression("parameters", str(index)))        
        
    def writeTransitionAction(self, transition, index):
        self.writer.beginMethod("%s_%i_exec" % (transition.parent_node.friendly_name, index))
        
        # parameters, start method
        self.writer.addFormalParameter("instance")
        self.writer.addFormalParameter("parameters")
        self.writer.beginMethodBody()

        # handle parameters to actually use them
        self.writeFormalEventParameters(transition)
        
        # write action
        transition.getAction().accept(self)
        
        # end method
        self.writer.endMethodBody()
        self.writer.endMethod()
        
    def writeTransitionGuard(self, transition, index):
        self.writer.beginMethod("%s_%i_guard" % (transition.parent_node.friendly_name, index))
        
        # parameters, start method
        self.writer.addFormalParameter("instance")
        self.writer.addFormalParameter("parameters")
        self.writer.beginMethodBody()
        
        # handle parameters to actually use them
        self.writeFormalEventParameters(transition)
        
        # get guard condition
        self.writer.startRecordingExpression()
        transition.getGuard().accept(self) # --> visit_Expression
        expr = self.writer.stopRecordingExpression()
        
        # return statement, end method
        self.writer.add(GLC.ReturnStatement(expr))
        self.writer.endMethodBody()
        self.writer.endMethod()
                
    # helper method
    def writeEnterHistory(self, entered_node, is_deep):
        ### OLD CODE (TODO)
        self.writer.beginMethod("enterHistory" + ("Deep" if is_deep else "Shallow") + "_" + entered_node.full_name)
        self.writer.beginMethodBody()

        self.writer.beginIf(GLC.EqualsExpression(
            GLC.ArrayLength(
                GLC.MapIndexedExpression(
                    GLC.SelfProperty("history_state"),
                    GLC.SelfProperty(entered_node.full_name))),
            "0"))
        defaults = entered_node.defaults

        for node in defaults:
            if node.is_basic :
                self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enter_"+node.full_name)))
            elif node.is_composite :
                self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enterDefault_"+node.full_name)))

        self.writer.endIf()
        self.writer.beginElse()
        children = entered_node.children
        if entered_node.is_parallel_state:
            for child in children:
                if not child.is_history :
                    self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enter_"+child.full_name)))
                    self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enterHistory"+("Deep" if is_deep else "Shallow")+"_"+child.full_name)))
        else:
            for child in children:
                if not child.is_history :
                    self.writer.beginIf(GLC.ArrayContains(
                        GLC.MapIndexedExpression(
                            GLC.SelfProperty("history_state"),
                            GLC.SelfProperty(entered_node.full_name)),
                        GLC.SelfProperty(child.full_name)))
                    if child.is_composite:
                        if is_deep :
                            self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enter_"+child.full_name)))
                            self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enterHistoryDeep_"+child.full_name)))
                        else :
                            self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enterDefault_"+child.full_name)))
                    else:
                        self.writer.add(GLC.FunctionCall(GLC.SelfProperty("enter_"+child.full_name)))
                    self.writer.endIf()
        self.writer.endElse()

        self.writer.endMethodBody()
        self.writer.endMethod()

    def visit_SelfReference(self, self_reference):
        self.writer.add(GLC.SelfExpression())

    def visit_StateReference(self, state_ref):
        self.writer.beginArray()
        for node in state_ref.getNodes():
            self.writer.add(GLC.SelfProperty(node.full_name))
        self.writer.endArray()

    def visit_InStateCall(self, in_state_call):
        self.writer.add(
            GLC.FunctionCall(
                GLC.Property("instance", "inState"),
                [
                    GLC.ArrayExpression(
                        [GLC.String(target_node.new_full_name) for target in in_state_call.targets for target_node in target.target_nodes]
                    )
                ]
            )
        )
        
    def visit_ElseGuard(self, else_guard):
        self.writer.add(
            GLC.String("ELSE_GUARD")
        )

    def visit_Expression(self, expression):
        self.writer.startRecordingExpression()
        self.writer.beginGlue()
        for part in expression.expression_parts:
            part.accept(self)
        self.writer.endGlue()
        expr = self.writer.stopRecordingExpression()
        self.writer.add(expr)

    def visit_ExpressionPartString(self, e):
        self.writer.add(e.string)
                    
    def visit_Script(self, script):
        self.writer.addRawCode(script.code)
        
    def visit_Log(self, log):
        self.writer.add(GLC.LogStatement(log.message))
        
    def visit_Assign(self, assign):
        self.writer.startRecordingExpression()
        assign.lvalue.accept(self) # --> visit_Expression
        lvalue = self.writer.stopRecordingExpression()
        self.writer.startRecordingExpression()
        assign.expression.accept(self) # --> visit_Expression
        rvalue = self.writer.stopRecordingExpression()
        self.writer.addAssignment(lvalue, rvalue)

