from PyQt5.QtCore import *
from settings.calc_conf import *
from widgets.node_base import *
from nodeeditor.utils import dumpException

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
DIR_CSS = DIR_MAIN + "/styles/qss" + "/"


class CalcInputContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("0", self)
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


@register_node(dict_OP_NODES.get("OP_NODE_INPUT"), CALC_NODES)
class CalcNode_Input(CalcNode):
    icon = DIR_ICONS + "in_b.png"
    op_code = dict_OP_NODES.get("OP_NODE_INPUT")
    op_title = "Входное"
    obj_title = "I1"
    content_label_objname = "calc_node_input"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = str(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        return self.value


@register_node(dict_OP_NODES.get("node_fogwing_iiot"), CALC_NODES)
class node_fogwing_iiot(CalcNode):
    icon = DIR_ICONS + "fogwing_logo.png"
    op_code = dict_OP_NODES.get("node_fogwing_iiot")
    op_title = "Fogwing IIoT Platform"
    obj_title = "FI1"
    content_label = "-----"
    content_label_objname = "node_fogwing_iiot_obj"
    obj_data = None
    obj_string = None

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()

    def initInnerClasses(self):
        from nodes.output import CalcOutputContent
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        u_value = self.value

        self.value = u_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        self.content.lbl.setText("%s" % self.content_label)
        return self.value


@register_node(dict_OP_NODES.get("node_blynkio"), CALC_NODES)
class node_blynkio(CalcNode):
    icon = DIR_ICONS + "blynkio_logo.png"
    op_code = dict_OP_NODES.get("node_blynkio")
    op_title = "Blynk IoT"
    obj_title = "BI1"
    content_label = "-----"
    content_label_objname = "node_blynkio_obj"
    obj_data = None
    obj_string = None

    def __init__(self, scene, inputs=[], outputs=[]):
        super().__init__(scene, inputs=inputs, outputs=outputs)
        self.eval()

    def initInnerClasses(self):
        from nodes.output import CalcOutputContent
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        u_value = self.value

        self.value = u_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()

        self.content.lbl.setText("%s" % self.content_label)
        return self.value

