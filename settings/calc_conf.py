LISTBOX_MIMETYPE = "application/x-item"

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_Expression = 3
OP_NODE_ADD = 4
OP_NODE_SUB = 5
OP_NODE_MUL = 6
OP_NODE_DIV = 7
OP_NODE_greater = 8
OP_NODE_less = 9
OP_NODE_some_thing = 10

dict_OP_NODES = {'OP_NODE_INPUT': 1,
                 'OP_NODE_OUTPUT': 2,
                 'OP_NODE_Expression': 3,
                 'OP_NODE_ADD': 4,
                 'OP_NODE_SUB': 5,
                 'OP_NODE_MUL': 6,
                 'OP_NODE_DIV': 7,
                 'OP_NODE_greater': 8,
                 'OP_NODE_less': 9,
                 'OP_NODE_some_thing_in': 10,
                 'OP_NODE_some_thing_out': 11
                 }


CALC_NODES = {
}

THING_NODES = {
}

ALL_NODES = [CALC_NODES, THING_NODES]
dict_ALL_NODES = {'CALC_NODES': CALC_NODES, 'THING_NODES': THING_NODES}


class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass


def register_node_now(op_code, class_reference, SELECT_NODES):
    # Добавляем модули узлов в "Логические узлы"
    if SELECT_NODES is None: return
    if op_code in SELECT_NODES:
        raise InvalidNodeRegistration("Duplicite node registration of '%s'. There is already %s" %(
            op_code, SELECT_NODES[op_code]
        ))
    SELECT_NODES[op_code] = class_reference


def register_node(op_code, SELECT_NODES, original_class=None):
    if original_class is not None:
        register_node_now(op_code, original_class, SELECT_NODES)
        return original_class

    def decorator(original_class):
        register_node_now(op_code, original_class, SELECT_NODES)
        return original_class
    return decorator


def get_class_from_opcode(op_code, select_nodes):
    if op_code not in select_nodes:
        raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return select_nodes[op_code]

# import all nodes and register them
from nodes import *