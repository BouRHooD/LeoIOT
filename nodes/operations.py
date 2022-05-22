from PyQt5.QtCore import *
from settings.calc_conf import *
from widgets.node_base import *
from nodeeditor.utils import dumpException

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__)))
DIR_ICONS = DIR_MAIN + "\styles\icons" + "\\"
DIR_CSS = DIR_MAIN + "\styles\qss" + "\\"


@register_node(dict_OP_NODES.get("OP_NODE_ADD"), CALC_NODES)
class CalcNode_Add(CalcNode):
    icon = DIR_ICONS + "add_b.png"
    op_code = dict_OP_NODES.get("OP_NODE_ADD")
    op_title = "Сложить"
    obj_title = "A1"
    content_label = "+"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        return input1 + input2


@register_node(dict_OP_NODES.get("OP_NODE_SUB"), CALC_NODES)
class CalcNode_Sub(CalcNode):
    icon = DIR_ICONS + "sub_b.png"
    op_code = dict_OP_NODES.get("OP_NODE_SUB")
    op_title = "Вычесть"
    obj_title = "S1"
    content_label = "-"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        return input1 - input2


@register_node(dict_OP_NODES.get("OP_NODE_greater"), CALC_NODES)
class CalcNode_greater_than(CalcNode):
    icon = DIR_ICONS + "_betterIcon.png"
    op_code = dict_OP_NODES.get("OP_NODE_greater")
    op_title = "Больше"
    obj_title = "GT1"
    content_label = ">"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        if (input1 > input2):
            return 1
        else:
            return 0


@register_node(dict_OP_NODES.get("OP_NODE_less"), CALC_NODES)
class CalcNode_less_than(CalcNode):
    icon = DIR_ICONS + "_lessIcon.png"
    op_code = dict_OP_NODES.get("OP_NODE_less")
    op_title = "Меньше"
    obj_title = "LT1"
    content_label = "<"
    content_label_objname = "calc_node_bg"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        if (input1 < input2):
            return 1
        else:
            return 0


# @register_node(dict_OP_NODES.get("OP_NODE_MUL"), CALC_NODES)
class CalcNode_Mul(CalcNode):
    icon = DIR_ICONS + "mul.png"
    op_code = dict_OP_NODES.get("OP_NODE_MUL")
    op_title = "Multiply"
    obj_title = "M1"
    content_label = "*"
    content_label_objname = "calc_node_mul"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        return input1 * input2

# @register_node(dict_OP_NODES.get("OP_NODE_DIV"), CALC_NODES)
class CalcNode_Div(CalcNode):
    icon = DIR_ICONS + "divide.png"
    op_code = dict_OP_NODES.get("OP_NODE_DIV")
    op_title = "Divide"
    obj_title = "D1"
    content_label = "/"
    content_label_objname = "calc_node_div"

    def evalOperation(self, input1, input2):
        input1 = int(input1)
        input2 = int(input2)
        return input1 / input2

# way how to register by function call
# register_node_now(OP_NODE_ADD, CalcNode_Add)