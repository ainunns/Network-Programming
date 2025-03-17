n = int(input())
mx = -9223372036854775808

for i in range(n):
  x = int(input())
  mx = max(mx, x)

print(mx)