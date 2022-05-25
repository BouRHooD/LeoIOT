from PyQt5.QtCore import *
from settings.calc_conf import *
from widgets.node_base import *
from nodeeditor.utils import dumpException

DIR_MAIN = os.path.dirname(os.path.abspath(str(sys.modules['__main__'].__file__))).replace("\\", "/")
DIR_ICONS = DIR_MAIN + "/styles/icons" + "/"
DIR_CSS = DIR_MAIN + "/styles/qss" + "/"


class Calc_some_thing_Content(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("1", self)
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


@register_node(dict_OP_NODES.get('OP_NODE_some_thing'), None)
class CalcNode_some_thing_in(CalcNode):
    # Стандартные настройки
    icon = "."
    op_code = dict_OP_NODES.get('OP_NODE_some_thing_in')
    op_title = "Вещь"
    obj_title = "T1"
    obj_port = None
    content_label_objname = "calc_node_some_thing_in"
    checked_send = False

    # Инициализируем экземпляр класса
    def __init__(self, scene, icon=".", op_code=dict_OP_NODES.get('OP_NODE_some_thing_in'), op_title="Вещь", obj_title="T0", obj_port=None):
        self.icon = icon
        self.op_code = op_code
        self.op_title = op_title
        self.obj_title = obj_title
        self.obj_port = obj_port
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = Calc_some_thing_Content(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def setText(self, _text):
        self.content.edit.setText(_text)

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


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.lbl = QLabel("0", self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setObjectName(self.node.content_label_objname)


class CalcNode_some_thing_out(CalcNode):
    # Стандартные настройки
    icon = "."
    op_code = dict_OP_NODES.get("OP_NODE_some_thing_out")
    op_title = "Вещь"
    obj_title = "T1"
    obj_port = None
    content_label_objname = "calc_node_some_thing_out"
    checked_send = False

    def __init__(self, scene, icon=".", op_code=dict_OP_NODES.get('OP_NODE_some_thing_out'), op_title="Вещь",
                 obj_title="T0", obj_port=None):
        self.icon = icon
        self.op_code = op_code
        self.op_title = op_title
        self.obj_title = obj_title
        self.obj_port = obj_port
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    def evalImplementation(self):
        input_node = self.getInput(0)
        if not input_node:
            self.grNode.setToolTip("Input is not connected")
            self.markInvalid()
            return

        val = input_node.eval()

        if val is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.content.lbl.setText("%s" % val)
        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")
        self.value = val
        return val