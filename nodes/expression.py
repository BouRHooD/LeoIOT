from PyQt5.QtCore import *
from settings.calc_conf import *
from widgets.node_base import *
from nodeeditor.utils import dumpException

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
DIR_CSS = DIR_MAIN + "/styles/qss" + "/"


class CalcExpressionContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("(1+1)>0", self)
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['value'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(dict_OP_NODES.get('OP_NODE_Expression'), CALC_NODES)
class CalcNode_Expression(CalcNode):
    icon = DIR_ICONS + "function.png"
    op_code = dict_OP_NODES.get('OP_NODE_Expression')
    op_title = "Выражение"
    content_label_objname = "calc_node_expression"

    def __init__(self, scene):
        super().__init__(scene, inputs=[3, 3, 4, 4], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcExpressionContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()

        answer_val = False
        if ">" in u_value or "<" in u_value or "<=" in u_value or ">=" in u_value:
            str_array_1 = u_value.split(">")
            str_array_2 = u_value.split("<")
            str_array_3 = u_value.split(">=")
            str_array_4 = u_value.split("<=")

            first_val = None
            second_val = None
            if len(str_array_1) > 1:
                first_val = str_array_1[0]
                second_val = str_array_1[1]

            if len(str_array_2) > 1:
                first_val = str_array_2[0]
                second_val = str_array_2[1]

            if len(str_array_3) > 1:
                first_val = str_array_3[0]
                second_val = str_array_3[1]

            if len(str_array_4) > 1:
                first_val = str_array_4[0]
                second_val = str_array_4[1]

            if first_val is not None and second_val is not None:
                first_val = first_val.replace("(", "").replace(")", "")
                second_val = second_val.replace("(", "").replace(")", "")

                first_equals_val = None
                if "+" in first_val:
                    first_val_array = first_val.split("+")
                    if len(first_val_array) > 1:
                        first_equals_val = float(first_val_array[0]) + float(first_val_array[1])

                elif "-" in first_val:
                    first_val_array = first_val.split("-")
                    if len(first_val_array) > 1:
                        first_equals_val = float(first_val_array[0]) - float(first_val_array[1])

                elif "*" in first_val:
                    first_val_array = first_val.split("*")
                    if len(first_val_array) > 1:
                        first_equals_val = float(first_val_array[0]) * float(first_val_array[1])

                elif "/" in first_val:
                    first_val_array = first_val.split("/")
                    if len(first_val_array) > 1:
                        if float(first_val_array[1]) != 0:
                            first_equals_val = float(first_val_array[0]) / float(first_val_array[1])
                        else:
                            first_equals_val = 0
                else:
                    first_equals_val = float(first_val)

                second_equals_val = None
                if "+" in second_val:
                    second_val_array = second_val.split("+")
                    if len(second_val_array) > 1:
                        second_equals_val = float(second_val_array[0]) + float(second_val_array[1])

                elif "-" in second_val:
                    second_val_array = second_val.split("-")
                    if len(second_val_array) > 1:
                        second_equals_val = float(second_val_array[0]) - float(second_val_array[1])

                elif "*" in second_val:
                    second_val_array = second_val.split("*")
                    if len(second_val_array) > 1:
                        second_equals_val = float(second_val_array[0]) * float(second_val_array[1])

                elif "/" in second_val:
                    second_val_array = second_val.split("/")
                    if len(second_val_array) > 1:
                        if float(second_val_array[1]) != 0:
                            second_equals_val = float(second_val_array[0]) / float(second_val_array[1])
                        else:
                            second_equals_val = float(0)
                else:
                    second_equals_val = float(second_val)

                if first_equals_val is not None and second_equals_val is not None:
                    if ">" in u_value: answer_val = first_equals_val > second_equals_val
                    if "<" in u_value: answer_val = first_equals_val < second_equals_val
                    if ">=" in u_value: answer_val = first_equals_val >= second_equals_val
                    if "<=" in u_value: answer_val = first_equals_val <= second_equals_val

        self.value = answer_val
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value