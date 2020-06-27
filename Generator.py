from pycfg.pycfg import PyCFG, CFGNode, slurp
import argparse
import tkinter as tk
from PIL import ImageTk, Image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('pythonfile', help='The python file to be analyzed')
    args = parser.parse_args()
    arcs = []

    cfg = PyCFG()
    cfg.gen_cfg(slurp(args.pythonfile).strip())
    g = CFGNode.to_graph(arcs)
    g.draw(args.pythonfile + '.png', prog='dot')

    # Draw using tkinter.
    root = tk.Tk()
    root.title("Control Flow Graph")
    img1 = Image.open(str(args.pythonfile) + ".png")  # PIL solution
    img1 = img1.resize((800, 600), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img1)

    background = "gray"

    panel = tk.Label(root, height=600, image=img)
    panel.pack(side="top", fill="both", expand="yes")
    nodes = g.number_of_nodes()  # no. of nodes.
    edges = g.number_of_edges()  # no. of Edges.
    complexity = edges - nodes + 2  # Cyclomatic complexity

    frame = tk.Frame(root, bg=background)
    frame.pack(side="bottom", fill="both", expand="yes")

    tk.Label(frame, text="Nodes\t\t" + str(nodes), bg=background).pack()
    tk.Label(frame, text="Edges\t\t" + str(edges), bg=background).pack()
    tk.Label(frame, text="Cyclo Complexity\t" +
                         str(complexity), bg=background).pack()

    root.mainloop()
