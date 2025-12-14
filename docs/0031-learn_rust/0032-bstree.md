# 0032:Rust 中的二叉搜索树

【未完待续】

1. 还是通过写代码来学习新语言符合我的习惯，写的过程中能感知到微妙的差别。
2. 这是第一个关于 rust 的笔记，所以会提到奇奇怪怪的内容
3. 二叉搜索树属于非常简单的内容，其实现不再赘述。

## 数据结构设计

1. 考虑到一个节点在任何时候都只有一个节点指向，所以使用 `Box` 作为指针非常合理。
2. 同时一个节点的左右子树可能为空，而 Box 本身不能为空，所以还需要使用 `Option` 在进行一次封装

故得到如下的数据定义，相较于 C/C++ ，明显复杂一些
```rust
struct BstreeNode<T> {
    pub val: T,
    pub left: Option<Box<BstreeNode<T>>>,
    pub right: Option<Box<BstreeNode<T>>>,
}
```

## Copy trait

在 C 中，实现 insert 或 delete 接口，需要考虑参数传递为 “引用传递” 还是 “拷贝传递”，一般而言会优先考虑设计为引用传递。

但是 rust 中，值传递有两种情况
1. 该类型有 `Copy trait` ，那么变量作为函数参数时，数据会被拷贝一份，调用后变量可以继续使用。
2. 该类型无 `Copy trait` ，那么变量为函数参数时，数据（也可能）会被拷贝一份（可能会被内联优化），但是调用后变量无法使用

一般而言，基本数据类型（如 i32, f64 等）都有 `Copy trait` ，而复杂数据类型，尤其是在堆上有内存使用的（如 String, Vec 等）则没有 `Copy trait` 。


## Option 中值的移动问题

还记得 [cloudflare 的崩溃事件么](https://blog.cloudflare.com/18-november-2025-outage/) ，在 Option 中无脑使用 `unwrap()` 获取其中的变量可能会导致崩溃。

![](attachments/Pasted%20image%2020251210232151.png)

并且根据一些工程实践，代码中应该完全禁用 `unwrap()` ，为此， rust 给了一个 `Some()` 语法用于获取 `Option` 中的值，例如

```rust
    pub fn insert(mut node: &mut Option<Box<BstreeNode<T>>>, val: T) -> bool {
        while let Some(n) = node {
        }
        
        /* More lines follow */
```


对于非引用类型的 `Option` 变量 ，使用 `Some()` 语法可能会导致 `Option` 变量中的值被移动（move），从而导致后续无法使用该 `Option` 变量。这和 `Copy trait` 有关。对于 `i32` 这样的有 `Copy trait` 的类型，使用 `Some()` 会是得值的一个拷贝，原 `Option` 变量仍然可以使用：
```rust
let op_int: Option<i32> = Some(1);

if let Some(mut val1) = op_int {
    val1 = 2;
    println!("Taken value: {val1}");
}

if op_int.is_some() {
    println!("{:?}", op_int.unwrap());
}
```
对于 `String` 这样的无 `Copy trait` 的类型，使用 `Some()` 会导致值被移动，原 `Option` 变量将无法再使用：
```rust
let op_string = Some("alpha".to_string());

if let Some(mut string_taken) = op_string {
    string_taken = "beta".to_string();
    println!("taken value: {}", string_taken);
}

// This is NOT OK 
// if op_string.is_some() {
//     println!("{:?}", op_string.unwrap());
// }
```

报错内容为
```txt
error[E0382]: borrow of partially moved value: `op_string`
  --> src/option_test.rs:29:12
   |
23 |         if let Some(mut string_taken) = op_string {
   |                     ---------------- value partially moved here
...
29 |         if op_string.is_some() {
   |            ^^^^^^^^^ value borrowed here after partial move
   |
   = note: partial move occurs because value has type `String`, which does not implement the `Copy` trait
```

这是一个典型的 `partial move` 错误。虽然 option 变量本身并没有被移动，但是其中的值被移动了，所以无法再使用该 option 变量。


为解决这个问题，我们可以获取 `Option` 变量中值的引用，从而避免值被移动，具体而言，有两种写法
```rust
let mut op_string_1 = Some("alpha".to_string());

// Method 1: using `ref mut`
// if let Some(ref mut val) = op_string_1 {

// Method 2: using `as_mut()`. More recommended
if let Some(val) = op_string_2.as_mut() {
    *val = "beta".to_string();
    println!("taken value of string_1: {}", val);
}

if op_string_1.is_some() {
    println!("value of string_1 {:?}", op_string_1.unwrap());
}
```

对于引用类型的 `Option` 变量，`as_mut` 也同样适用。实际上，`as_mut` 的官方介绍为 "Converts from &mut Option<T> to Option<&mut T>"，但是对于非引用的 `Option` 变量而言，`as_mut` 会自动生成一个可变引用。所以，如下的代码无法通过编译，因为有两次可变借用：

```rust
let mut op_string_3 = Some("aaa".to_string());

if let Some(val) = op_string_3.as_mut() {
    *val = "bbb".to_string();
    println!("value of string_3: {}", val);

    if let Some(val2) = op_string_3.as_mut() {
        *val2 = "ccc".to_string();
        println!("value of string_3: {}", val2);
    }

    *val = "ddd".to_string();
}
```

但是，如果去掉 `*val = "ddd".to_string();` ，则可以通过编译。原因是，现代 `rust` 通过变量最后使用的位置判断生命周期，如果没有 `*val = "ddd".to_string();` ,`val` 的生命周期在第一次 `print` 后就结束了，所以不会冲突。

### 类型嵌套

例如：`node: &mut Option<Box<BstreeNode<T>>>` , mut意味着内部的所有东西都可以改，例如可以做一下操作：

```rust
if let Some(box_ref) = node {
    if let Some(node_ref) = box_ref {
        // some code
    }
}
```


## 并非完善的借用规则检查
某些代码可能没有违背借用规则检查，但是无法通过编译，例如我需要删除值最大的节点：

```rust
fn extract_max(mut node: &mut Option<Box<BstreeNode<T>>>) -> T {
    //This is NOT OK since node is borrowed inside the loop
    while let Some(r) = node {       // `r` borrows from `node`
        if r.right.is_some() {
            node = &mut r.right;     // `r` must stay alive for this assignment
        } else {
            break;                   // `r` still considered borrowed after break
        }
    }

    let mut max_node = node.take().expect("fail to get the max value");
    *node = max_node.left.take();

    max_node.val
}
```

这里的核心问题是，node 在退出循环后，仍然被认为是被借用的状态，从而导致后续的 `take()` 操作无法进行。对比下面的代码：

```rust
pub fn insert(mut node: &mut Option<Box<BstreeNode<T>>>, val: T) -> bool {
    while let Some(n) = node {
        match val.cmp(&n.val) {
            std::cmp::Ordering::Less => node = &mut n.left,
            std::cmp::Ordering::Greater => node = &mut n.right,
            std::cmp::Ordering::Equal => return false,
        }
    }

    *node = Some(BstreeNode::new(val));
    true
}
```

`insert` 函数可以通过编译，原因在于循环退出后，node 一定是 `None`，所以不存在借用的问题。

所以这是一个非常难受的限制，目前我知道的，最好的实现 `extract_max` 的方式为（非递归），但是这种实现方式仍会使用 `expect` （虽然提前做了检查）。当然递归的写法更加简洁，但是有栈溢出的问题。

```rust
if node.is_none() {
    panic!("extract_max called on empty node");
}

while node.as_ref().is_some_and(|n| n.right.is_some()) {
    node = &mut node.as_mut().expect("parano check").right;
}
```


## 生命周期的绑定：
在bstree中，如果要通过值得到一个节点的可变引用，需要声明一个类似的函数

```rust
fn get_target_node_mut(
    mut node: &mut Option<Box<BstreeNode<T>>>,
    val: &T,
) -> Option<&mut Option<Box<BstreeNode<T>>>>
```

但是该函数无法通过编译，报错内容为：

```txt
missing lifetime specifier
this function's return type contains a borrowed value, but the signature does not say whether it is borrowed from `node` or `val`
```

这是因为 rust 无法确定返回值的生命周期到底是和 `node` 相关还是和 `val` 相关，解决方案为增加生命周期的绑定：

```rust
fn get_target_node_mut<'a>(
    mut node: &'a mut Option<Box<BstreeNode<T>>>,
    val: &T,
) -> Option<&'a mut Option<Box<BstreeNode<T>>>>
```

可以通过如下经典案例来说明函数中生命周期绑定的必要性：

```rust
fn main() {
    let long_lived = String::from("I am global-ish");
    let result;

    {
        let short_lived = String::from("I die soon");
        
        // We call a function here...
        result = pick_best(&long_lived, &short_lived); 
    } // <--- `short_lived` is dropped (freed) here!

    // DANGER ZONE: 
    // If `result` points to `short_lived`, accessing it here crashes the program.
    // If `result` points to `long_lived`, accessing it here is safe.
    println!("Result is: {}", result); 
}
```

在实现中，可以使用 `?` 来简化代码:

```rust
let ordering: std::cmp::Ordering = val.cmp(&node.as_ref()?.val);
```
`?` 在这里的含义为：如果 `node` 为 `None` ，则调用函数直接返回 `None`，继续执行。这也要求函数的返回值为 `Option` 类型。

## rust 的先进性

### trait 的使用
在模版编程中，trait 会要求变量具有特定的性质，使得模版的作用范围更加明确。例如：

```rust
impl<T: std::cmp::Ord> BstreeNode<T> {
```

可以要求类型 `T` 具有 `Ord` trait，从而可以使用 `<` , `>` 等比较操作符。同时，在实现的内部，可以某些函数具有更多的 trait 限制，例如:

```rust
pub fn print_sub_tree<W: Write>(
    writer: &mut W,
    node: &Box<BstreeNode<T>>,
    indent: i32,
    tag: &str,
) where
    T: std::fmt::Display,
```

可以要求类型 `T` 可以被格式化输出，从而可以使用 `{}` 进行打印。


### Option 类型
在我目前的视角中，Option 解决的最大问题是，是应该由调用者或是有函数实现去判断一个指针是否为空，也起到了提醒开发者注意空指针的作用。
