---
title: 0032:Rust 中的二叉搜索树
---
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

引用传递就相对简单（么？）。

## 封装的代价：（及其）繁琐的代码

### Option

还记得 [cloudflare 的崩溃事件么](https://blog.cloudflare.com/18-november-2025-outage/) ，在 Option 中无脑使用 `unwrap()` 获取其中的变量可能会导致崩溃。

![](attachments/Pasted%20image%2020251210232151.png)

并且根据一些工程实践，代码中应该完全禁用 `unwrap()` ，为此， rust 给了一个 `Some()` 语法用于获取 `Option` 中的值。

```rust
    pub fn insert(mut node: &mut Option<Box<BstreeNode<T>>>, val: T) -> bool {
        while let Some(n) = node {
        /* More lines follow */
```