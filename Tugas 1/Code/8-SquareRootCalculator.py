import math
n = int(input())

x = math.sqrt(n)

if(x*x == n):
  print(int(x))
else:
  print("Not a perfect square")