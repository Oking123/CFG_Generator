x = 0
y = 0
signal = [True]
if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]):
    print(1)
if grid[x][y] == 1:
    print(1)
else:
    if x == 0 or x == len(grid) - 1 or y == 0 or y == len(grid[0]) - 1:
        signal[0]= False
    grid[x][y] = 1
    travel(x - 1, y, signal)
    travel(x + 1, y, signal)
    travel(x, y - 1, signal)
    travel(x, y + 1, signal)
