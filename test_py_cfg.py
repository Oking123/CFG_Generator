from py_cfg import CFGBlock, PyCFG
import unittest
import ast


class Test_CFGBlock(unittest.TestCase):
    def test_creation(self):
        CFGBlock.reset()
        p = CFGBlock(ast_node=ast.parse("print(1)"))
        self.assertEqual(p.children, [])
        start = CFGBlock(ast_node=ast.parse("start"))
        self.assertEqual(start.source_code(), "start")

    def test_equal(self):
        CFGBlock.reset()
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        self.assertFalse(a == b)
        b.rid = a.rid
        self.assertTrue(a == b)

    def test_cache(self):
        CFGBlock.reset()
        for key, block in CFGBlock.cache.items():
            self.assertEqual(CFGBlock.cache[block.rid], block)

    def test_addchild(self):
        CFGBlock.reset()
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        a.add_child(b)
        self.assertEqual(a.children, [b])

    def test_addparent(self):
        CFGBlock.reset()
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
        CFGBlock.reset()
        a = CFGBlock(ast_node=ast.parse("print(1)"))
        b = CFGBlock(ast_node=ast.parse("print(1)"))
        b.add_parent(a)
        CFGBlock.update_children()
        self.assertTrue(b in a.children)


class Test_Pycfg(unittest.TestCase):
    def test_module(self):
        pycfg = PyCFG()
        code = \
"""
a = 1
b = 1
c = 1
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 5)

    def test_assign(self):
        pycfg = PyCFG()
        code = \
"""
a = 2
b = a
c = a
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),5)

    def test_if(self):
        pycfg = PyCFG()
        code = \
"""
a = 3
if a < 2:
    print (a)
else:
    print (5)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),6)

    def test_expr(self):
        pycfg = PyCFG()
        code = \
"""
print(a)
b
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),4)

    def test_while(self):
        pycfg = PyCFG()
        code = \
"""
a = 5
while a > 3:
    print (a)
    a = a - 1
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),6)

    def test_constant(self):
        pycfg = PyCFG()
        code = \
"""
print(1)
3
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),4)

    def test_operator(self):
        pycfg = PyCFG()
        code = \
"""
a = 1
b = 2
c = a + b
d = a - b
e = a * b
f = a / b
g = a % b
h = a // b
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 10)

        pycfg = PyCFG()
        code = \
"""
a = 1
b = 2
c = call(a) + call(b)
d = call(a) - call(b)
e = call(a) * call(b)
f = call(a) / call(b)
g = call(a) % call(b)
h = call(a) // call(b)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 10)

    def test_compare(self):
        pycfg = PyCFG()
        code = \
"""
a = 1
b = 2
c = a > b
d = a < b
print(a == b)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 7)

    def test_augassign(self):
        pycfg = PyCFG()
        code = \
"""
a = 1
b = 2
b -= a
b += a
b *= a
b /= a
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 8)

        pycfg = PyCFG()
        code = \
"""
a = 1
a += call(a)
a -= call(a)
a *= call(a)
a /= call(a)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 7)

    def test_for(self):
        pycfg = PyCFG()
        code = \
"""
a = [1,2,3,4]
b = 0
for i in range(len(a)):
    b = b + a[i]
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),6)

    def test_pass(self):
        pycfg = PyCFG()
        code = \
"""
a = [1,2,3,4]
b = 0
for i in range(len(a)):
    if a[i] == 2:
        pass
    else:
        b = b + a[i]
    print(b)
print(a)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),10)

    def test_continue(self):
        pycfg = PyCFG()
        code = \
"""
a = 0
for i in range(0,10):
    if i == 1:
        continue
    else:
        a = a + i
    print(a)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),8)

    def test_break(self):
        pycfg = PyCFG()
        code = \
"""
a = 0
for i in range(0,10):
    if i == 8:
        break
    else:
        a = a + i
    print(a)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),8)

    def test_if_for(self):
        pycfg = PyCFG()
        code = \
"""
a = 0
if a > 0:
    for i in range(1,10):
        a = a + i
else:
    print(a)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),7)

    def test_while_if_for(self):
        pycfg = PyCFG()
        code = \
"""
a = [1,2,3,4,5]
b = 0
while b < 100:
    for i in range(len(a)):
        if a[i] != 3:
            b = b +a [i]
        else:
            b = b*2
print(b)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),10)

    def test_bitoperate(self):
        pycfg = PyCFG()
        code = \
"""
a = 1
a >> 1
a << 1
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache), 5)

        pycfg = PyCFG()
        code = \
"""
a = 1
a >> call(a)
a << call(b)
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),5)


    def test_define_call(self):
        pycfg = PyCFG()
        code = \
"""
def find(a,b):
    if b < 0:
        return a+b
    else:
        return a-b
a = 3
b = 4
print(find(a,find(a,b)),find(a,b))
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),13)
        self.assertTrue(CFGBlock.cache[8].children[0].rid == 9)
        self.assertTrue(CFGBlock.cache[8].children[1].rid == 11)
        self.assertTrue(CFGBlock.cache[8].children[2].rid == 12)
        self.assertTrue(CFGBlock.cache[9].children[0].rid == 10)


    def test_recursion(self):
        pycfg = PyCFG()
        code = \
"""
def find(a,b):
    if b < 0:
        return 1
    a += b
    b -= 1
    return find(a,b)+a
c = 1
c = find(find(c,c),find(c,c))	
"""
        pycfg.generate_cfg(code)
        self.assertEqual(len(CFGBlock.cache),15)
        self.assertTrue(CFGBlock.cache[10].children[0].rid == 11)
        self.assertTrue(CFGBlock.cache[11].children[0].rid == 12)
        self.assertTrue(CFGBlock.cache[11].children[1].rid == 13)



if __name__ == '__main__':
    unittest.main()
