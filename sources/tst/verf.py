def verf(a, b):
    if (a* (a+b+1))%10 == b%10:
        print a, b, (a+b+1)

for i in range (0, 9):
    for j in range (0, 9):
        verf(i,j)
