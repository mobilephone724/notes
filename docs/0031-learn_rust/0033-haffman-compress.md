# Experience with Huffman Compression



ON GOING

## Introduction

This is the second rust repo I wrote to practice rust. It is far more different
from bstree and While finishing it, I know more features of rust.

## BitVec





### What is iter?

`pub fn iter(&self) -> Iter<'_, u8, Msb0>`

##type encapsulation

While I try to use `BitVec<u8, Msb0>;` to represent a compressed value, I code it as below subconsciously:

```rust
pub type CompressedContent = BitVec<u8, Msb0>;
```

But it isn't a good  idea here. This means that **I can't implement  more functions on this type**, and `BitVec` itself doesn't have a `Copy` trait, but I need to get the it left, right value in huffman tree while generating the character map.



To handle this issue, I use another method ==> 

```rust
pub struct HaffmanCompressedCode {
    pub val: BitVec<u8, Msb0>,
}
```

However, this comes to more issues, such as I must  implement much more function for using in `HashMap`. But thanks to `derive`, I can do it easily since `BitVec` itself has all the implements I want.

```rust
#[derive(Clone, PartialEq, Eq, Hash)]
pub struct HaffmanCompressedCode {
    pub val: BitVec<u8, Msb0>,
}
```

Note that not all attributes can be derived.  From [official doc](https://doc.rust-lang.org/rust-by-example/trait/derive.html)

> The following is a list of derivable traits:
>
> * Comparison traits: [`Eq`](https://doc.rust-lang.org/std/cmp/trait.Eq.html), [`PartialEq`](https://doc.rust-lang.org/std/cmp/trait.PartialEq.html), [`Ord`](https://doc.rust-lang.org/std/cmp/trait.Ord.html), [`PartialOrd`](https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html).
> * [`Clone`](https://doc.rust-lang.org/std/clone/trait.Clone.html), to create `T` from `&T` via a copy.
> * [`Copy`](https://doc.rust-lang.org/core/marker/trait.Copy.html), to give a type 'copy semantics' instead of 'move semantics'.
> * [`Hash`](https://doc.rust-lang.org/std/hash/trait.Hash.html), to compute a hash from `&T`.
> * [`Default`](https://doc.rust-lang.org/std/default/trait.Default.html), to create an empty instance of a data type.
> * [`Debug`](https://doc.rust-lang.org/std/fmt/trait.Debug.html), to format a value using the `{:?}` formatter.

## File operation





read u8 into u64 and `Vec<u64>`

