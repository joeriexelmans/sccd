import re
import abc
from typing import List, Tuple
from sccd.execution.statechart_instance import *

# TODO: Clean this mess up. Look at all object management operations and see how they can be improved.
class ObjectManager(Instance):
    _regex_pattern = re.compile("^([a-zA-Z_]\w*)(?:\[(\d+)\])?$")

    def __init__(self, model):
        self.model = model

        # set of all instances in the runtime
        # we need to maintain this set in order to do broadcasts
        self.instances = [self] # object manager is an instance too!

        i = StatechartInstance(model.get_default_class(), self)
        self.instances.append(i)

    def _create(self, class_name) -> StatechartInstance:
        # Instantiate the model for each class at most once:
        # The model is shared between instances of the same type.
        statechart = self.model.classes[class_name]
        i = StatechartInstance(statechart, self)
        self.instances.append(i)
        return i

    def initialize(self, now: Timestamp) -> List[OutputEvent]:
        return []

    # Implementation of super class: Instance
    def big_step(self, timestamp: Timestamp, input_events: List[Event]) -> List[OutputEvent]:
        output = []
        for e in input_events:
            try:
                o = ObjectManager._handlers[e.name](self, timestamp, e.parameters)
                if isinstance(o, OutputEvent):
                    output.append(o)
                elif isinstance(o, list):
                    output.extend(o)
            except KeyError:
                pass
        return output

    # def _assoc_ref(self, input_string) -> List[Tuple[str,int]]:
    #     if len(input_string) == 0:
    #         raise AssociationReferenceException("Empty association reference.")
    #     path_string =  input_string.split("/")
    #     result = []
    #     for piece in path_string:
    #         match = ObjectManager._regex_pattern.match(piece)
    #         if match:
    #             name = match.group(1)
    #             index = match.group(2)
    #             if index is None:
    #                 index = -1
    #             result.append((name,int(index)))
    #         else:
    #             raise AssociationReferenceException("Invalid entry in association reference. Input string: " + input_string)
    #     return result
            
    def _handle_broadcast(self, timestamp, parameters) -> OutputEvent:
        if len(parameters) != 2:
            raise ParameterException ("The broadcast event needs 2 parameters (source of event and event name).")
        return OutputEvent(parameters[1], InstancesTarget(self.instances))

    # def _handle_create(self, timestamp, parameters) -> List[OutputEvent]:
    #     if len(parameters) < 2:
    #         raise ParameterException ("The create event needs at least 2 parameters.")

    #     source = parameters[0]
    #     association_name = parameters[1]
        
    #     traversal_list = self._assoc_ref(association_name)
    #     instances = self._get_instances(source, traversal_list)
        
    #     association = source.associations[association_name]
    #     # association = self.instances_map[source].getAssociation(association_name)
    #     if association.allowedToAdd():
    #         ''' allow subclasses to be instantiated '''
    #         class_name = association.to_class if len(parameters) == 2 else parameters[2]
    #         instance = self._create(class_name)
    #         # new_instance = self.model.classes[class_name](parameters[3:])
    #         if not instance:
    #             raise ParameterException("Creating instance: no such class: " + class_name)
    #         output_events = instance.initialize(timestamp)
    #         try:
    #             index = association.addInstance(instance)
    #         except AssociationException as exception:
    #             raise RuntimeException("Error adding instance to association '" + association_name + "': " + str(exception))
    #         p = instance.associations.get("parent")
    #         if p:
    #             p.addInstance(source)
    #         return output_events.append(OutputEvent(Event("instance_created", None, [association_name+"["+str(index)+"]"]), InstancesTarget([source])))
    #     else:
    #         return OutputEvent(Event("instance_creation_error", None, [association_name]), InstancesTarget([source]))

    # def _handle_delete(self, timestamp, parameters) -> OutputEvent:
    #     if len(parameters) < 2:
    #         raise ParameterException ("The delete event needs at least 2 parameters.")
    #     else:
    #         source = parameters[0]
    #         association_name = parameters[1]
            
    #         traversal_list = self._assoc_ref(association_name)
    #         instances = self._get_instances(source, traversal_list)
    #         # association = self.instances_map[source].getAssociation(traversal_list[0][0])
    #         association = source.associations[traversal_list[0][0]]
            
    #         for i in instances:
    #             try:
    #                 for assoc_name in i["instance"].associations:
    #                     if assoc_name != 'parent':
    #                         traversal_list = self._assoc_ref(assoc_name)
    #                         instances = self._get_instances(i["instance"], traversal_list)
    #                         if len(instances) > 0:
    #                             raise RuntimeException("Error removing instance from association %s, still %i children left connected with association %s" % (association_name, len(instances), assoc_name))
    #                 # del i["instance"].controller.input_ports[i["instance"].narrow_cast_port]
    #                 association.removeInstance(i["instance"])
    #                 self.instances.remove(i["instance"])
    #             except AssociationException as exception:
    #                 raise RuntimeException("Error removing instance from association '" + association_name + "': " + str(exception))
    #             i["instance"].user_defined_destructor()
    #             i["instance"].stop()
            
    #         return OutputEvent(Event("instance_deleted", parameters = [parameters[1]]), InstancesTarget([source]))
                
    # def _handle_associate(self, timestamp, parameters) -> OutputEvent:
    #     if len(parameters) != 3:
    #         raise ParameterException ("The associate_instance event needs 3 parameters.")
    #     else:
    #         source = parameters[0]
    #         to_copy_list = self._get_instances(source, self._assoc_ref(parameters[1]))
    #         if len(to_copy_list) != 1:
    #             raise AssociationReferenceException ("Invalid source association reference.")
    #         wrapped_to_copy_instance = to_copy_list[0]["instance"]
    #         dest_list = self._assoc_ref(parameters[2])
    #         if len(dest_list) == 0:
    #             raise AssociationReferenceException ("Invalid destination association reference.")
    #         last = dest_list.pop()
    #         if last[1] != -1:
    #             raise AssociationReferenceException ("Last association name in association reference should not be accompanied by an index.")
                
    #         added_links = []
    #         for i in self._get_instances(source, dest_list):
    #             association = i["instance"].associations[last[0]]
    #             if association.allowedToAdd():
    #                 index = association.addInstance(wrapped_to_copy_instance)
    #                 added_links.append(i["path"] + ("" if i["path"] == "" else "/") + last[0] + "[" + str(index) + "]")
            
    #         return OutputEvent(Event("instance_associated", parameters = [added_links]), InstancesTarget([source]))
                
    # def _handle_disassociate(self, timestamp, parameters) -> OutputEvent:
    #     if len(parameters) < 2:
    #         raise ParameterException ("The disassociate_instance event needs at least 2 parameters.")
    #     else:
    #         source = parameters[0]
    #         association_name = parameters[1]
    #         if not isinstance(association_name, list):
    #             association_name = [association_name]
    #         deleted_links = []
            
    #         for a_n in association_name:
    #             traversal_list = self._assoc_ref(a_n)
    #             instances = self._get_instances(source, traversal_list)
                
    #             for i in instances:
    #                 try:
    #                     index = i['ref'].associations[i['assoc_name']].removeInstance(i["instance"])
    #                     deleted_links.append(a_n +  "[" + str(index) + "]")
    #                 except AssociationException as exception:
    #                     raise RuntimeException("Error disassociating '" + a_n + "': " + str(exception))
            
    #         return OutputEvent(Event("instance_disassociated", parameters = [deleted_links]), InstancesTarget([source]))
        
    # def _handle_narrowcast(self, timestamp, parameters) -> OutputEvent:
    #     if len(parameters) != 3:
    #         raise ParameterException ("The narrow_cast event needs 3 parameters.")
    #     source, targets, cast_event = parameters
        
    #     if not isinstance(targets, list):
    #         targets = [targets]

    #     all_instances = []
    #     for target in targets:
    #         traversal_list = self._assoc_ref(target)
    #         instances = self._get_instances(source, traversal_list)
    #         all_instances.extend(instances)
    #     return OutputEvent(cast_event, instances)
        
    # def _get_instances(self, source, traversal_list):
    #     print("_get_instances(source=",source,"traversal_list=",traversal_list)
    #     currents = [{
    #         "instance": source,
    #         "ref": None,
    #         "assoc_name": None,
    #         "assoc_index": None,
    #         "path": ""
    #     }]
    #     # currents = [source]
    #     for (name, index) in traversal_list:
    #         nexts = []
    #         for current in currents:
    #             association = current["instance"].associations[name]
    #             if (index >= 0 ):
    #                 try:
    #                     nexts.append({
    #                         "instance": association.instances[index],
    #                         "ref": current["instance"],
    #                         "assoc_name": name,
    #                         "assoc_index": index,
    #                         "path": current["path"] + ("" if current["path"] == "" else "/") + name + "[" + str(index) + "]"
    #                     })
    #                 except KeyError:
    #                     # Entry was removed, so ignore this request
    #                     pass
    #             elif (index == -1):
    #                 for i in association.instances:
    #                     nexts.append({
    #                         "instance": association.instances[i],
    #                         "ref": current["instance"],
    #                         "assoc_name": name,
    #                         "assoc_index": index,
    #                         "path": current["path"] + ("" if current["path"] == "" else "/") + name + "[" + str(index) + "]"
    #                     })
    #                 #nexts.extend( association.instances.values() )
    #             else:
    #                 raise AssociationReferenceException("Incorrect index in association reference.")
    #         currents = nexts
    #     return currents

    _handlers = {
        # "narrow_cast": _handle_narrowcast,
        "broad_cast": _handle_broadcast,
        # "create_instance": _handle_create,
        # "associate_instance": _handle_associate,
        # "disassociate_instance": _handle_disassociate,
        # "delete_instance": _handle_delete
    }
