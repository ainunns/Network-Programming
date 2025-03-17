n = int(input())

if(n < 2):
  print("Not Prime")
  exit()

p = 2
while (p*p <= n):
  if(n % p == 0):
    print("Not Prime")
    exit()

  p += 1

print("Prime")