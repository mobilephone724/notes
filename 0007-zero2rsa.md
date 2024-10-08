---
title: "ZERO TO RSA"
author: "mobilephone724"
math: true
---

## 从0证明RSA


RSA 算法（即一个非对称加密算法）除了应用非常广泛外，其特性也非常吸引人（起码非常吸引我）。我在网上找了很多关于RSA的证明，要么不够详细（例如缺失对前置定理的证明），要么需要引出较多复杂的数论概念。作者本身水平不高，试图绕过这些复杂的概念，从初等数学的开始，完备地证明RSA。

关于RSA的背景知识可能很多，可以慢慢阅读，我在此尝试从初等数学开始证明。这些背景知识的证明有一定的顺序，如果读者发现某个证明看不懂，可以向前翻阅。

参考的文章如下：（因为参考的文章太多，大概率不全）


- [费马小定理](https://zh.wikipedia.org/wiki/%E8%B4%B9%E9%A9%AC%E5%B0%8F%E5%AE%9A%E7%90%86)
- [中国剩余定理](https://zh.wikipedia.org/wiki/%E4%B8%AD%E5%9B%BD%E5%89%A9%E4%BD%99%E5%AE%9A%E7%90%86)
- [阮一峰的博客——RSA算法原理（一）](https://www.ruanyifeng.com/blog/2013/07/rsa_algorithm_part_two.html)
- [阮一峰的博客——RSA算法原理（二）](https://www.ruanyifeng.com/blog/2013/06/rsa_algorithm_part_one.html)
- [初等数论笔记Part 1： 欧拉定理](https://zhuanlan.zhihu.com/p/35060143)
- [算法学习笔记(9)：逆元](https://zhuanlan.zhihu.com/p/100587745)

## 费马小定理

### 简介

如果 $p$ 是质数且 $\mathrm{gcd}(a,p)=1$ , 那么 $a^{p-1}\equiv 1\ (\mathrm{mod}\ p)$

在证明该定理前，先证明一个简单的引理

### 引理1

如果 $p$ 是质数，且 $\mathrm{gcd}(a,p)=1$ , 那么

$$
\lbrace ka \ \mathrm{mod}\ p | k = \lbrace 1,2,...,p -1 \rbrace \rbrace= \lbrace 1,2,3,...,p-1 \rbrace
$$

即二者存在一对一的关系。由于这两个集合的元素个数相同，所以只要证明左侧集合没有重复元素即可

证明：假设存在 $k_1$ 和 $k_2$ 满足 $1 \leq k_1 < k_2 \leq p-1$ ，且 $k_1a\ \mathrm{mod}\ p = k_2a\ \mathrm{mod}\ p$ . 那么可知

$$
(k_1+p-k_2)a\ \mathrm{mod}\ p = pa\ \mathrm{mod}\ p=0
$$

即 $(k_1+p-k_2)a\ \mathrm{mod}\ p=0$ 。由于 $p$ 是质数，那么 $(k_1+p-k_2)a$ 一定是 $p$​​ 的倍数，这显然不可能。



### 证明费马小定理

$$
\begin{align}
(1a)(2a)(3a)...((p-1)a)\ \mathrm{mod}\ p &= (a^{p-1}(p-1)!)\ \mathrm{mod}\ p \newline
(1a\ \mathrm{mod}\ p)(2a\ \mathrm{mod}\ p)...((p-1)a\ \mathrm{mod}\ p) &=  (a^{p-1}(p-1)!)\ \mathrm{mod}\ p\newline
(p-1)! &= (a^{p-1}(p-1)!)\ \mathrm{mod}\ p
\end{align}
$$

整理得 $a^{p-1}\equiv 1\ (\mathrm{mod}\ p)$​



## 模逆元

### 简介

定义： $a$ 对 $n$ 的**模逆元**是满足 $ab\equiv 1\ (\mathrm{mod}\ n)$ 的 $b$​

**模逆元的存在性**：模逆元存在的充要条件是 $\mathrm{gcd}(a,n)=1$​

为证明该存在性定理，需要先证明引理2

### 引理2

若 $\mathrm{gcd}(a,n)=g$ ，则存在 $x,y\in Z$，满足 $ax+ny=g$

证明：

- 设集合 $S=\lbrace ax+ny|x,y\in Z \rbrace $，显然，存在 $s\in S$ 并且 $s>0$
- 设 $d$ 为 $S$ 中最小的，大于 $0$ 的元素
- 若 $a\ \mathrm{mod}\ p\neq 0$ ，则存在 $k,r$ 满足 $a=kd+r$ ，其中 $0 < r < k$ ，带入 $d=ax_0+ny_0$ ，得到 $r=a(1-kx_0)+n(-ky_0)$ 。 显然 $r\in S$ ，又 $0 < r < k$ ，这与 $d$ 为 $S$ 中最小的大于 $0$ 的假设不符。
- 故 $a\ \mathrm{mod}\ d=0$ ，同理 $n\ \mathrm{mod}\ d=0$
- 所以 $d$ 为 $a$ 和 $n$ 共同的因数。设 $g=ld$ ， $l\geq0$ 且 $l\in Z$ ，那么有 $g=ld=a(lx_0)+n(ly_0)$ 。

### 证明模逆元

现在证明模逆元

充分性

- 已知 $\mathrm{gcd}(a,n)=1$ ，则有 $1=ax_0+ny_0$
- $(ax_0+ny_0)\ \mathrm{mod}\ n = ax_0 \ \mathrm{mod}\ n $​
- $(ax_0+ny_0)\ \mathrm{mod}\ n= 1 \ \mathrm{mod}\ n=1$
- 故 $ax_0 \ \mathrm{mod}\ n=1$ 即 $ax_0\ \equiv 1\ (\mathrm{mod}\ n)$ ， $b=x_0$

必要性：

- 已经存在 $b$ 满足 $ab\ \equiv 1\ (\mathrm{mod}\ n)$​
- 则存在 $y,k$ 满足 $(ab+ny)\ \mathrm{mod}\ n=1$
- 则存在 $k$ 满足 $ab+ny-1=kn$
- 即 $ab + n(y-k)=1$
- 根据**引理2**，有 $\mathrm{gcd}(a,n)\leq 1$ ，显然只有 $\mathrm{gcd}(a,n)=1$

## 中国剩余定理

方程组

$$
\begin{equation}
\begin{cases}
x\ \equiv a_1\ (\mathrm{mod}\ m_1)\newline
x\ \equiv a_2\ (\mathrm{mod}\ m_2)\newline
...\newline
x\ \equiv a_n\ (\mathrm{mod}\ m_n)\newline
\end{cases}
\end{equation}
$$

其中对于任意 $i\neq j$ 有 $\mathrm{gcd}(m_i,m_j)=1$ ，对于任意 $a_1,a_2,...,a_n$ 有解。

证明：如下

存在性

- 令 $M=m_1m_2,...m_n=\prod\limits_{i=1}^{n}m_i$， $M_i=M/m_i$
- 显然有 $\mathrm{gcd}(M_i,m_i)=1$ ，故存在 $t_i$ 满足 $M_it_i\ \equiv 1\ (\mathrm{mod}\ m_i)$
- 故对于 $x\ \equiv a_1\ (\mathrm{mod}\ m_1)$ ，有 $a_iM_it_i\ \equiv a_i\ (\mathrm{mod}\ m_i)$
- 故可得 $x$ 的一个解 $x=\sum\limits_{i=1}^{n}a_iM_it_i$

完备性

- 若 $x_1,x_2$ 都是方程组的解，那么对于任意 $i\in \lbrace 1,2,...,n \rbrace$ ，有 $(x_1-x_2)\ \mathrm{mod}\ m_i=0$
- 故 $x_1-x_2=kM$
- 所以通解为 ${kM+}\sum\limits_{i=1}^{n}a_iM_it_i$



## 欧拉公式

### 简介

- 函数 $\phi(n)$ 为 $\lbrace 1,2,...,n \rbrace$ 中和 $n$ 互质的数的数量
- 例如 $\phi(8)=4$ ，因为 $\mathrm{gcd}(\lbrace 1,3,5,7 \rbrace,4)=1$

### 性质

**（性质1）**

对于质数 $n$ ，有 $\phi(n)=n-1$

**（性质2）**


若存在质数 $p$ 满足 $n=p^k$ ，则 $\phi(n)=p^k-p^k/p=n(1-1/p)$ 。思路为 $\lbrace 1,2,...,n \rbrace$ 中除去 $p$ 的倍数

**（性质3）**

若 $\mathrm{gcd}(m,n)=1$ ，则 $\phi(mn)=\phi(m)\phi(n)$ ​。证明如下：

- 对于任意 $0 < N < mn$ ，有 $N=k_1m+p=k_2n+q$ 。假设 $N$ 满足 $\mathrm{gcd}(N,mn)=1$
- 显然， $\mathrm{gcd}(N,m)=1$ ，故 $\mathrm{gcd}(k_1m+p,m)=1$ ，显然 $\mathrm{gcd}(p,m)=1$ 。同理 $\mathrm{gcd}(q,n)$ 。
- 对于方程组

$$
\begin{equation}
\begin{cases}
N\ \equiv p\ (\mathrm{mod}\ m)\newline
N\ \equiv q\ (\mathrm{mod}\ n)
\end{cases}
\end{equation}
$$

根据中国剩余定理，有解 $N=kmn+t_ppn+t_qqm$ 。

每有一组 $(p,q)$ ，该方程组就有一个解。注意 $\mathrm{gcd}(p,m)=1$ ,且 $\mathrm{gcd}(q,n)$ 。

**（性质4）**

对于 $n=\prod\limits_{i=1}^rp_i^{k_i}$ ，有 $\phi(n)=\phi(\prod\limits_{i=1}^rp_i^{k_i})=\prod\limits_{i=1}^r\phi(p_i^{k_i})=\prod\limits_{i=1}^r(n(1-1/p_i))=n^r\prod\limits_{i=1}^r(1-1/p_i)$

## 欧拉定理

### 简介

若 $n,a$ 为正整数，且 $\mathrm{gcd}(n,a)=1$ 则 $a^{\phi(n)}\ \equiv 1\ (\mathrm{mod}\ n)$​

### 欧拉定理的证明

设 $\Phi(n)=\lbrace c_1,c_2,...,c_{\phi(n)} \rbrace$ 为小于 $n$ 且与 $n$ 互质的数的集合，即 $\mathrm{gcd}(c_i,n)=1$。

若 $\mathrm{gcd}(a,n)=1$ ，考虑集合 $\Phi_a(n)=\lbrace (ac_1)\ \mathrm{mod}\ n,(ac_2)\ \mathrm{mod}\ n,...,(ac_{\phi(n)})\ \mathrm{mod}\ n \rbrace$ 。我们证明 $\Phi(n)=\Phi_a(n)$

先证明 $\Phi_a(n)$ 中没有重复的元素，若 $ac_i\ \equiv ac_j\ (\mathrm{mod}\ n)$ ,则 $c_i\ \equiv c_j\ (\mathrm{mod}\ n)$ ，这显然错误。

再证明 $\mathrm{gcd}(ac_i\ \mathrm{mod}\ n, n)=1$ 。设 $ac_i=k_in+r_i$ ，若 $\mathrm{gcd}(r_i,n)=g$ ，则 $ac_i=g(k_i(n/g)+(r_i/g))$ 。等式右侧是 $g$ 的倍数，而左侧显然不是（ $a$ 和 $c$ 都与 $n$ 互质）

所以：

$$
\prod\limits_{i=1}^{\phi(n)}c_i \ \equiv \prod\limits_{i=1}^{\phi(n)}c_ia(\ \mathrm{mod}\ n)
$$


即

$$
\prod\limits_{i=1}^{\phi(n)}c_i \ \equiv a^{\phi(n)}\prod\limits_{i=1}^{\phi(n)}c_i(\ \mathrm{mod}\ n)
$$

显然 $\mathrm{gcd}(\prod\limits_{i=1}^{\phi(n)}c_i,n)=1$

故

$$
a^{\phi(n)}\ \equiv 1\ (\mathrm{mod}\ n)
$$



## RSA算法

### 算法流程

1. 生成秘钥
   1. 选择连个大质数 $p$ 和 $q$ ，计算 $n=p * q$ 
   2. 计算 $\phi(n)=(p-1)(q-1)$ 
   3. 选择正整数 $e$ 满足 $1 < e < \phi(n)$ ，且 $\mathrm{gcd}(e,\phi(n))=1$
   4. 计算 $e$ 对 $\phi(n)$ 的模逆元 $d$ ，即 $ed\ \equiv 1\ (\mathrm{mod}\ \phi(n))$
   5. 得到公钥对 $(n,e)$ ，私钥对 $(n, d)$
2. 加密
   1. 加密的数为 $m$ ，满足 $0\leq m < n$
   2. 计算 $c=m^e\ \mathrm{mod}\ n$ ，则 $c$ 就是密文
3. 解密
   1. $m=c^d\ \mathrm{mod}\ n$

### 算法证明

显然，核心点在于证明 $m=c^d\ \mathrm{mod}\ n$​ 。

简答化简可得， $c^d\ \mathrm{mod}\ n=(m^e\ \mathrm{mod}\ n)^d\ \mathrm{mod}\ n=m^{ed}\ \mathrm{mod}\ n$​

根据 $ed\ \equiv 1\ (\mathrm{mod}\ \phi(n))$ ，可知存在 $k$ 使得 $ed=k\phi(n)+1$ ，带入 $m^{ed}\ \mathrm{mod}\ n$ 得，

$$
\begin{align}
m^{ed}\ \mathrm{mod}\ n&= m^{k\phi(n)+1}\ \mathrm{mod}\ n \newline
                       &= ((m^{\phi(n)} \mathrm{mod}\ n)^k*(m\ \mathrm{mod}\ n))\ \mathrm{mod}\ n \newline
                       &= (m(m^{\phi(n)} \mathrm{mod}\ n)^k) \ \mathrm{mod}\ n
\end{align}
$$

#### 通常情况

当 $\mathrm{gcd}(m,n)=1$ 时（即 $m\neq hp$ 且 $m\neq hq$ 时），根据欧拉定理 $m^{\phi(n)}\ \equiv 1\ (\mathrm{mod}\ n)$ ，可知 $m^{\phi(n)} \mathrm{mod}\ n=1$​

则 $m^{ed}\ \mathrm{mod}\ n = m\ \mathrm{mod}\ n=m$ 

#### 特殊情况

当 $m=hp$ 时，（ $m=hq$ 同理）有 $m^{\phi(n)} \mathrm{mod}\ n = (hp)^{(p-1)(q-1)}\mathrm{mod}\ pq$

而因为 $q$ 是质数，根据费马小定理，有 $((hp)^{k(p-1)})^{q-1}\ \equiv 1\ (\mathrm{mod}\ q)$ 。故

$$
\begin{align}
((hp)^{k(p-1)})^{q-1}hp\ &\equiv hp\ (\mathrm{mod}\ q) \newline
(hp)^{k(p-1)(q-1)+1}\ &\equiv hp\ (\mathrm{mod}\ q) \newline
(hp)^{(cd)}\ &\equiv hp\ (\mathrm{mod}\ q)
\end{align}
$$

故存在 $t$ 满足

$$
(hp)^{ed}=tq+hp
$$


注意，等式左侧是 $p$ 的倍数，而 $p$ 是质数，故 $t$ 必定是 $p$ 的倍数，设 $t=t'p$ ，则

$$
\begin{align}
(hp)^{ed}&=t'pq+hp=t'n+hp \newline
m^{ed}\ &\equiv m\ (\mathrm{mod}\ n) \newline
m^{ed-1} \ &\equiv 1\ (\mathrm{mod}\ n) \newline
m^{k\phi(n)} \ &\equiv 1\ (\mathrm{mod}\ n)
\end{align}
$$

同理 $m^{ed}\ \mathrm{mod}\ n = (m(m^{\phi(n)} \mathrm{mod}\ n)^k) \ \mathrm{mod}\ n = m\ \mathrm{mod}\ n=m$