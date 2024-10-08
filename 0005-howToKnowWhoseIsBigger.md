---
weight: 3
title: "Alice and Bob how to know whose number is bigger without giving away their own's"
draft: false
author: "mobilephone724"
# description: "Hugo provides multiple built-in shortcodes for author convenience and to keep your markdown content clean."
tags: ["Zero—Knowledge Proof"]
categories: ["cryptology"]
math: true

lightgallery: true
toc:
  enable: true
  auto: true
date: 2022-01-14T23:43:08+08:00
publishDate: 2022-01-14T23:43:08+08:00
---



## Definiteness：

Suppose Alice has number $i$ and Bob has number $j$ and $1\leq i,j \leq 9$. We need a protocol for them to decide whether $i < j$ in the end(aside from their own values)

## Solution:

Let $M$ be the set of all $N$-bit nonnegative integers

Let $Q_N$ be the set of all one-one and onto function from $M$ to $M$ 

1. Alice generates a public key from $Q_N$, called $E_a$, and the inverse function of $E_a$ is $D_a$
2. Bob picks a random value $x \in M$, compute $k = E_a(x)$, then send $k - j$ to Alice
3. Alice computes $y_u=D_a(k - j + u)$ for $u = 1,2,\dots,9$
4. Alice generates a random prime $p$ of $N/2$-bit, and computes $z_u=y_u(\mod p)$ for all $u$.
5. Alice repeats step 4 until all $z_u$ differ by at least 2 in the $\mod p$ sense
6. Alice sends the $p$ and $z_1,z_2,\dots,z_i,z_{i+1}+1,\dots,z_{9} +1$ (all in $\mod p$ sense)to Bob
7. Bob looks at the $j$-th value(not counting p) sent from Alice, and decides that $i\geq j$ if it is equal to $x \mod p$, or $i<j$ otherwise

