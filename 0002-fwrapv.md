---
title: "\"-fwrapv\" option in gcc"
date: 2024-08-05T21:30:13+08:00
---

[c - What does -fwrapv do? - Stack Overflow](https://stackoverflow.com/questions/47232954/what-does-fwrapv-do)

`-fwrapv` tells the compiler that overflow of signed integer arithmetic must be treated as well-defined behavior, even though it is undefined in the C standard.

It has two meaning full results:

1. INT_MAX + 1 is overflowed to INT_MIN correctly. This is almost the default behavior in gcc.
2. Don’t let the compiler assume `x + 1 > x`.

See the program below

```bash
╭─ycz at 9f38a58b120d in /home/dev 24-08-05 - 13:28:02
╰─○ cat test.c
#include <stdio.h>

#define INT_MAX 0x7FFFFFFF

static int compare(int x) {return x + 1 > x;}

int main()
{
    int x = 0;
    printf("%d is bigger than %d?\n%d\n", x + 1, x, compare(x));
    x = INT_MAX;
    printf("%d is bigger than %d?\n%d\n", x + 1, x, compare(x));

    return 0;
}
╭─ycz at 9f38a58b120d in /home/dev 24-08-05 - 13:28:06
╰─○ gcc test.c && ./a.out 
1 is bigger than 0?
1
-2147483648 is bigger than 2147483647?
1
╭─ycz at 9f38a58b120d in /home/dev 24-08-05 - 13:28:13
╰─○ gcc test.c -fwrapv && ./a.out 
1 is bigger than 0?
1
-2147483648 is bigger than 2147483647?
0
```


