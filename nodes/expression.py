from PyQt5.QtCore import *
from settings.calc_conf import *
from widgets.node_base import *
from nodeeditor.utils import dumpException

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__)))
DIR_ICONS = DIR_MAIN + "\styles\icons" + "\\"
DIR_CSS = DIR_MAIN + "\styles\qss" + "\\"


class CalcExpressionContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("(1+1)>0", self)
        self.edit.setAlignment(Qt.AlignRight)
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


#@register_node(dict_OP_NODES.get(OP_NODE_Expression))
class CalcNode_Expression(CalcNode):
    icon = DIR_ICONS + "in_b.png"
    op_code = dict_OP_NODES.get(OP_NODE_Expression)
    op_title = "Выражение"
    content_label_objname = "calc_node_expression"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcExpressionContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = int(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value