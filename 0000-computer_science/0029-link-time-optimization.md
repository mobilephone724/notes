# conception

**Link Time Optimization** (LTO, **`-flto`** option in compilation) is a technique that allows the compiler to perform optimizations at the linking stage, rather than just during the compilation of individual files. This can result in better performance and more efficient code.

## What is LTO (Link Time Optimization)?

- **Standard Compilation**: Normally, when compiling a program, each source file (.c, .cpp) is compiled into an object file (.o), and then these object files are linked together to create the final executable. During this process, the compiler only optimizes code at the individual file level.
- LTO: With Link Time Optimization, the compiler **retains intermediate representations of the code in the object files** (instead of just machine code) and performs additional optimization during the linking phase. This allows the compiler to optimize the entire program as a whole, not just on a per-file basis.

##  Key Benefits
- Cross-module optimization
- Smaller code size
- Better performance

## Downsides

- Longer build times
- Increased memory usage during compilation


# Example

Take the code below as an example:

```C
/* main.c ================== */
#include "utils.h"

int main() {
    int a = 10;
    int b = 20;
    int result = add(a, b);  // Calling function from utils.c
    return result;
}
/* main.c end ================== */



/* utils.c ================== */
#include "utils.h"

int add(int x, int y) {
    return x + y;
}
/* utils.c end ================== */



/* utils.h */
int add(int x, int y);
/* utils.h end ================== */

```



## without `lto`

1. **Compilation** of `main.c`, The compiler compiles the code in main.c but only knows that there’s a function `add()` being used. It doesn't know what `add()` does **so the compiler cannot inline the `add()` function or optimize the function call away**.
2. **Compilation** of `utils.c` . The compiler compiles utils.c, but since add() is not used in utils.c, the compiler cannot optimize it further
3. **Linking**: The linker takes the compiled object files (main.o and utils.o) and links them together into an executable. **At this stage, no optimization can happen to combine or inline the `add()` function into `main()` because the optimization was limited to each translation unit**.

## With LTO

1. **Compilation** of main.c and utils.c with `-flto`: Instead of generating machine code, the compiler **retains intermediate representations** (IR) for both main.c and utils.c, **postponing the final code generation until the linking phase**.
2. Linking with -flto: During linking, the compiler now has a global view of both main() and add(). It can see that add() is just a small, simple function (a single addition), and **may decide to inline the add() function directly into main()**.

## validation

```bash
gcc --version
gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0
Copyright (C) 2021 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Compile without `flto`.  (`-O0` option seem to force the compilor too stupid)
```bash
gcc main.c utils.c -O1
objdump -d a.out > without_flto.asm
```

see the `without_flto.asm` file
```asm
0000000000000714 <main>:
 714:	a9bf7bfd 	stp	x29, x30, [sp, #-16]!
 718:	910003fd 	mov	x29, sp
 71c:	52800281 	mov	w1, #0x14                  	// #20
 720:	52800140 	mov	w0, #0xa                   	// #10
 724:	94000003 	bl	730 <add>
 728:	a8c17bfd 	ldp	x29, x30, [sp], #16
 72c:	d65f03c0 	ret

0000000000000730 <add>:
 730:	0b010000 	add	w0, w0, w1
 734:	d65f03c0 	ret
```

---
Compile with `flto`, the computation seem to be finished during compilation 
```bash
gcc main.c utils.c -O1 -flto
objdump -d a.out > with_flto.asm
```

```asm
0000000000000714 <main>:
 714:	528003c0 	mov	w0, #0x1e                  	// #30
 718:	d65f03c0 	ret

// No add() function completely
```

