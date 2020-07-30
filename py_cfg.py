import ast
import astunparse
import pygraphviz


class CFGBlock:
    registry = 0
    cache = {}
    stack = []

    def __init__(self, parents=None, ast_node=None):
        """

        :param parents: [CFGBlock]
        :param ast_node: ast_node
        """
        if parents is None:
            parents = []
        self.parents = parents
        self.ast_node = ast_node
        self.rid = CFGBlock.registry
        self.children = []
        self.cache[self.rid] = self
        CFGBlock.registry += 1

        if hasattr(self.ast_node, 'lineno'):
            self.lineno = self.ast_node.lineno
        else:
            self.lineno = 0

    def source_code(self):
        """

        :return: str
        """
        return astunparse.unparse(self.ast_node).strip()

    def __str__(self):
        result = str(self.rid) + ": "
        result += "line" + str(self.lineno) + ': '
        result += self.source_code()
        result += " children: ["
        if self.children:
            for child in self.children:
                result += str(child.rid) + ','
            result = result[:-1]
        result += ']'
        return '{' + result + '}'

    def __eq__(self, other):
        return self.rid == other.rid

    def add_child(self, child):
        """

        :param child: CFGBlock
        :return: None
        """
        if child not in self.children:
            self.children.append(child)

    def set_parent(self, parent):
        self.parents = parent

    def add_parent(self, parent):
        """

        :param parent: CFGBlock
        :return:
        """
        if parent not in self.parents:
            self.parents.append(parent)

    def add_parents(self, parents):
        for parent in parents:
            self.add_parent(parent)

    @classmethod
    def to_graph(cls):
        G = pygraphviz.AGraph(directed=True)
        for rid, node in CFGBlock.cache.items():
            G.add_node(rid)
            temp = G.get_node(rid)
            temp.attr['label'] = str(node.rid) + ":" + node.source_code()
        for rid, node in CFGBlock.cache.items():
            for parent in node.parents:
                G.add_edge(G.get_node(parent.rid), G.get_node(rid))
        return G

    @classmethod
    def update_children(cls):
        for node in CFGBlock.cache.values():
            for parent in node.parents:
                parent.add_child(node)

    @classmethod
    def show_blocks(cls):
        for node in CFGBlock.cache.values():
            print(node)


class PyCFG:
    def __init__(self):
        self.start = CFGBlock(ast_node=ast.parse("start"))

    def generate_cfg(self, python_code):
        ast_node = ast.parse(python_code)
        self.walk(ast_node, [self.start])
        CFGBlock.update_children()

    def draw_cfg(self):
        g = CFGBlock.to_graph()
        g.layout()
        g.draw("temp.png", prog='dot')

    def walk(self, node, myparents):
        parent = myparents
        if node.__class__.__name__.lower() == 'module':
            parent = self.on_module(node, myparents)
            return parent
        elif node.__class__.__name__.lower() == 'assign':
            parent = self.on_assign(node, myparents)
            return parent
        return parent

    def on_module(self, node, myparents):
        p = myparents
        for item in node.body:
            p = self.walk(item, p)
        return p

    def on_assign(self, node, myparents):
        temp = CFGBlock(ast_node=node, parents=myparents)
        p = self.walk(node.value, [temp])
        return p



code =\
"""
a = 1
b = 1
c = a + b
"""
# a = ast.parse(code)
# print(ast.dump(a))
# for node in a.body:
#     print(astunparse.unparse(node))


g = PyCFG()
g.generate_cfg(code)
g.draw_cfg()
CFGBlock.show_blocks()

# start = CFGBlock(ast_node=ast.parse("start"))
# a = CFGBlock(ast_node=ast.parse("print('hello world')"))
# a.add_parent(start)
# b = CFGBlock(ast_node=ast.parse("a > b"))
# c = CFGBlock(ast_node=ast.parse("print('hello world2')"))
# b.add_parent(a)
# c.add_parent(a)
# CFGBlock.update_children()
# g = CFGBlock.to_graph()
# for knode in CFGBlock.cache.values():
#     print(knode)
# g.layout()
# g.draw("temp.png", prog='dot')
