grid = [[1,1,1,1,1,1,1,0],[1,0,0,0,0,1,1,0],[1,0,1,0,1,1,1,0],[1,0,0,0,0,1,0,1],[1,1,1,1,1,1,1,0]]
isisland = True


# def travel(x, y, signal):
#     if x < 0 or x >= len(grid) or y < 0 or y >= len(grid[0]):
#         return
#     if grid[x][y] == 1:
#         return
#     else:
#         if x == 0 or x == len(grid) - 1 or y == 0 or y == len(grid[0]) - 1:
#             signal[0]= False
#         grid[x][y] = 1
#         travel(x - 1, y, signal)
#         travel(x + 1, y, signal)
#         travel(x, y - 1, signal)
#         travel(x, y + 1, signal)


ans = 0
signal = [True]
for i in range(len(grid)):
    for j in range(len(grid[0])):
        if grid[i][j] == 0:
            signal = [True]
            travel(i, j, signal)
            if signal[0]:
                ans += 1
print(ans)