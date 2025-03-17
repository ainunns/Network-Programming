d = {}

n = int(input())
for i in range(n):
    key, value = input().split()
    d[key] = value

key = input()
print(d[key])