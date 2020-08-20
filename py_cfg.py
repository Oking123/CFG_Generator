import ast
import astunparse
import pygraphviz


class CFGBlock:
    registry = 0          # an unique ID for all CFGBlock in a CFG graph, written as rid
    cache = {}            # a cache using a dictionary, key is the rid and value is the CFGBlock
    y_branch = set()
    function = set()
    call_return = set()

    def __init__(self, parents=None, ast_node=None):
        """

        :param parents: [CFGBlock]
        :param ast_node: ast_node
        """
        if parents is None:
            parents = []
        assert type(parents) is list
        self.parents = parents
        self.ast_node = ast_node
        self.rid = CFGBlock.registry
        self.children = []
        self.cache[self.rid] = self
        CFGBlock.registry += 1
        for parent in self.parents:
            parent.add_child(self)

        if hasattr(self.ast_node, 'lineno'):
            self.lineno = self.ast_node.lineno
        else:
            self.lineno = 0

    def source_code(self):
        """

        :return: str
        """
        return astunparse.unparse(self.ast_node).strip().strip('_')

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
            parent.add_child(self)

    def add_parents(self, parents):
        for parent in parents:
            self.add_parent(parent)

    @classmethod
    def to_graph(cls):
        G = pygraphviz.AGraph(directed=True)
        for rid, node in CFGBlock.cache.items():
            G.add_node(rid)
            temp = G.get_node(rid)
            temp.attr['label'] = str(node.lineno) + ":" + node.source_code()
        for rid, node in CFGBlock.cache.items():
            for parent in node.parents:
                if (parent.rid, rid) in CFGBlock.y_branch:
                    G.add_edge(G.get_node(parent.rid), G.get_node(rid), label="Y")
                else:
                    G.add_edge(G.get_node(parent.rid), G.get_node(rid))
        for pid, cid in CFGBlock.call_return:
            G.add_edge(G.get_node(pid), G.get_node(cid), style='dashed')
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

    @classmethod
    def reset(cls):
        CFGBlock.cache.clear()
        CFGBlock.y_branch.clear()
        CFGBlock.function.clear()
        CFGBlock.call_return.clear()
        CFGBlock.registry = 0


class PyCFG:
    def __init__(self):
        CFGBlock.reset()
        self.start = CFGBlock(ast_node=ast.parse("start"))

    def generate_cfg(self, python_code):
        ast_node = ast.parse(python_code)
        nodes = self.walk(ast_node, [self.start])
        end = CFGBlock(ast_node=ast.parse("end"), parents=nodes)
        CFGBlock.update_children()

    def draw_cfg(self):
        g = CFGBlock.to_graph()
        g.layout()
        g.draw("temp.png", prog='dot')

    def walk(self, node, myparents):
        """

        :param node: ast_node
            which is the current code executing
        :param myparents: list(CFGBlock)
            the parent CFGBlock of the current running state
        :return: list(CFGBlock)
            the current [CFGBlock]
        """
        if node is None:
            return
        parent = myparents
        call_function = "on_" + node.__class__.__name__.lower()
        if hasattr(self, call_function):
            fc = getattr(self, call_function)
            parent = fc(node, myparents)
        # else:
        #     parent = [CFGBlock(ast_node=ast.parse(node), parents=myparents)]
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

    def on_if(self, node, myparents):
        condition = ast.parse("_if:" + astunparse.unparse(node.test).strip())
        if_node = CFGBlock(ast_node=condition, parents=myparents)
        if_node.lineno = node.lineno
        if_branch = [if_node]
        for temp in node.body:
            if_branch = self.walk(temp, if_branch)
        else_branch = [if_node]
        if hasattr(node, 'orelse'):
            for temp in node.orelse:
                else_branch = self.walk(temp, else_branch)
        CFGBlock.y_branch.add((if_node.rid, if_node.children[0].rid))
        self.walk(node.test, [if_node])
        return if_branch + else_branch

    def on_expr(self, node, myparents):
        expr_node = [CFGBlock(ast_node=node, parents=myparents)]
        return self.walk(node.value, expr_node)

    def on_while(self, node, myparents):
        condition = ast.parse("_while:" + astunparse.unparse(node.test).strip())
        while_node = CFGBlock(ast_node=condition, parents=myparents)
        while_node.break_point = []
        while_node.lineno = node.lineno
        p = [while_node]
        for temp in node.body:
            p = self.walk(temp, p)
        CFGBlock.y_branch.add((while_node.rid, while_node.children[0].rid))
        while_node.add_parents(p)
        return while_node.break_point + [while_node]

    def on_constant(self, node, myparents):
        return myparents

    def on_for(self, node, myparents):
        for_condition = "_for:" + astunparse.unparse(node.target).strip() + ' in ' + astunparse.unparse(node.iter)
        for_node = CFGBlock(ast_node=ast.parse(for_condition), parents=myparents)
        for_node.break_point = []
        for_node.lineno = node.lineno
        self.walk(node.iter, [for_node])
        p = [for_node]
        for temp in node.body:
            p = self.walk(temp, p)
        for_node.add_parents(p)
        return for_node.break_point + [for_node]

    def on_pass(self, node, myparents):
        return [CFGBlock(ast_node=node, parents=myparents)]

    def on_continue(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, "break_point"):
            parent = parent.parents[0]
        continue_node = CFGBlock(ast_node=node, parents=myparents)
        parent.add_parent(continue_node)
        return []

    def on_break(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, "break_point"):
            parent = parent.parents[0]
        break_node = CFGBlock(ast_node=node, parents=myparents)
        parent.break_point.append(break_node)
        return []

    def on_call(self, node, myparents):
        if type(node.func) is ast.Name and node.func.id in CFGBlock.function:
            ast_node = ast.parse("_call:" + astunparse.unparse(node))
            call_node = CFGBlock(ast_node=ast_node, parents=myparents)
            call_node.lineno = node.lineno
            p = [call_node]
            CFGBlock.call_return.add((call_node.rid, myparents[0].rid))
            # myparents[0].add_parent(call_node)
            for arg in node.args:
                self.walk(arg, p)
            return myparents
        else:
            for arg in node.args:
                self.walk(arg, myparents)
            return myparents

    def on_binop(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.right, left)
        return right

    def on_compare(self, node, myparents):
        left = self.walk(node.left, myparents)
        right = self.walk(node.comparators[0], left)
        return right

    def on_unaryop(self, node, myparents):
        return self.walk(node.operand, myparents)

    def on_augassign(self, node, myparents):
        temp = CFGBlock(ast_node=node, parents=myparents)
        p = self.walk(node.value, [temp])
        return p

    def on_functiondef(self, node, myparents):
        CFGBlock.function.add(node.name)
        start_string = "start: {}({})".format(node.name, astunparse.unparse(node.args))
        start_node = CFGBlock(ast_node=ast.parse(start_string))
        start_node.return_points = []
        end_node = CFGBlock(ast_node=ast.parse("end: {}".format(node.name)))
        p = [start_node]
        for item in node.body:
            p = self.walk(item, p)
        end_node.add_parents(p+start_node.return_points)
        return myparents

    def on_return(self, node, myparents):
        parent = myparents[0]
        while not hasattr(parent, 'return_points'):
            parent = parent.parents[0]
        return_node = CFGBlock(ast_node=node, parents=myparents)
        p = [return_node]
        self.walk(node.value, p)
        parent.return_points.append(return_node)
        return []

#
# code = \
# """
# for i in range(10):
#     if i == 1:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
#     elif i == 2:
#         continue
# print(2)
# """
#
# g = PyCFG()
# CFGBlock.function.add("find")
# g.generate_cfg(code)
# g.draw_cfg()
# CFGBlock.show_blocks()
