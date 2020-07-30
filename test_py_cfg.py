from py_cfg import CFGBlock
import unittest
import ast


class Test_CFGBlock(unittest.TestCase):
    def test_creation(self):
        p = CFGBlock(ast_node=ast.parse("print(1)"))
        self.assertEqual(str(p), "{line0: print(1) children: []}")
        start = CFGBlock(ast_node=ast.parse("start"))
        self.assertEqual(start.source_code(), "start")

    def test_equal(self):
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        self.assertFalse(a == b)
        b.rid = a.rid
        self.assertTrue(a == b)

    def test_cache(self):
        for key, block in CFGBlock.cache.items():
            self.assertEqual(CFGBlock.cache[block.rid], block)

    def test_addchild(self):
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        a.add_child(b)
        self.assertEqual(a.children, [b])

    def test_addparent(self):
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        c = CFGBlock(ast_node=ast.parse("print(1)"))
        a.set_parent([b, c])
        self.assertEqual(a.parents, [b, c])
        a.add_parent(a)
        self.assertEqual(a.parents, [b, c, a])
        a.add_parents([b, c])
        self.assertEqual(a.parents, [b, c, a])
        a.set_parent([a])
        self.assertEqual(a.parents, [a])
        a.add_parents([b, c])
        self.assertEqual(a.parents, [a, b, c])

    def test_updatechildren(self):
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        b.add_parent(a)
        CFGBlock.update_children()
        self.assertTrue(b in a.children)



if __name__ == '__main__':
    unittest.main()
