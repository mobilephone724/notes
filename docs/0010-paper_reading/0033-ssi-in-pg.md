这是一篇针对 PostgreSQL 内核研发团队定制的深度技术分享博客。基于你提供的论文《Serializable Snapshot Isolation in PostgreSQL》以及你的补充要求（详细解释 Write Skew、SI 定义及危险结构的理论证明），我重新梳理了内容。

这篇文档旨在作为组内分享的讲稿大纲，保持了工业界的务实风格，兼顾理论深度与工程实现的 Trade-off。

------

# PostgreSQL 内核分享：SSI (Serializable Snapshot Isolation) 原理、证明与实现

**Author:** Kernel Dev Team

**Target:** PostgreSQL 9.1+ Kernel Architecture

**Ref:** *Serializable Snapshot Isolation in PostgreSQL (VLDB '12)*

## 1. 为什么我们需要 SSI？从 SI 的局限性说起

在深入代码之前，我们需要对齐两个核心概念：**Snapshot Isolation (SI)** 和 **Write Skew (写偏斜)**。这也是 SSI 诞生的原点。

### 1.1 什么是 Snapshot Isolation (SI)？

在 PostgreSQL 中，`REPEATABLE READ` 隔离级别对应就是标准的 SI。

* **定义：** 事务 $T$ 在启动（或第一条语句）时创建一个快照（Start-Timestamp）。事务内的所有读操作，都只能看到该时间点之前已提交的数据。
* **写规则（First-Committer-Wins）：** 如果 $T_1$ 和 $T_2$ 并发修改同一行数据，先提交者成功，后者必须 Abort（在 PG 中通过 Tuple Lock 和 Update 时的 Xmax 检查实现）。
* **优势：** 读写互不阻塞，避免了脏读、不可重复读和幻读（PG 的 SI 实现通过快照可见性天然避免了幻读）。

### 1.2 SI 搞不定的异常：写偏斜 (Write Skew)

虽然 SI 看起来很完美，但它允许一种被称为“写偏斜”的异常，导致数据破坏。

**经典案例：医生值班 (Doctors Duty)**

假设规则：医院至少需要一名医生值班。

当前状态：Alice 和 Bob 都在值班。

| **Transaction T1 (Alice)**                                | **Transaction T2 (Bob)**                                |
| --------------------------------------------------------- | ------------------------------------------------------- |
| `IF count(on_call) >= 2` (读到 2)                         | `IF count(on_call) >= 2` (读到 2)                       |
| `UPDATE doctors SET on_call = false WHERE name = 'Alice'` | `UPDATE doctors SET on_call = false WHERE name = 'Bob'` |
| **Commit**                                                | **Commit**                                              |

* **在 SI 下：** $T_1$ 和 $T_2$ 读的都是事务开始时的快照（都有2人值班）。且 $T_1$ 修改的是 Alice 的行，$T_2$ 修改的是 Bob 的行。**没有写冲突（WW-Conflict）**，所以两者都能提交。
* **结果：** 0 人值班。违反了业务约束。
* **本质：** 两个事务读取了**重叠**的数据集合，但修改了**不相交**的数据集合。S2PL（两阶段锁）可以通过共享锁阻塞写锁来避免此问题，但 SI 无法检测。

## 2. 理论核心：如何证明“危险结构”？

SSI 的核心不在于“全量检测环”，而在于“检测可能形成环的结构”。这基于 Fekete 等人的理论发现。

### 2.1 依赖图与边的类型

我们将历史看作一个图，节点是事务，边代表依赖关系（操作顺序）：

1. **wr-dependency (写读依赖):** $T_1$ 写，$T_2$ 读到了 $T_1$ 的版本。意味着 $T_1$ 在 $T_2$ 之前。
2. **ww-dependency (写写依赖):** $T_1$ 写，$T_2$ 覆盖了 $T_1$ 的版本。意味着 $T_1$ 在 $T_2$ 之前。
3. **rw-antidependency (读写反向依赖):** $T_1$ 读了一个旧版本，$T_2$ 随后（或并发）生成了新版本。
   * **关键点：** 在串行化顺序中，因为 $T_1$ 没看到 $T_2$ 的修改，所以 $T_1$ 看起来像是在 $T_2$ 之前执行的。但实际上 $T_2$ 是并发或稍后运行的。我们记作 $T_1 \xrightarrow{rw} T_2$。

### 2.2 为什么必须是两条相邻的 rw 边？

**定理：** 任何序列化异常（图中的环）必然包含结构 $T_1 \xrightarrow{rw} T_2 \xrightarrow{rw} T_3$。

**推导证明逻辑 (Proof Intuition)：**

1. **环的存在性：** 如果存在异常，图中一定有环。
2. **边的性质：**
   * `wr` 和 `ww` 边通常意味着时间上的先后顺序。如果 $T_1 \to T_2$ 是 wr 或 ww 关系，通常意味着 $T_1$ 在 $T_2$ 开始前（或提交前）已经提交了。它们符合正常的“时间流向”。
   * `rw` 边是唯一允许“时间倒流”或“并发交错”的边。$T_1$ 读旧数据，$T_2$ 写新数据。虽然逻辑上 $T_1$ 在前，但物理时间上 $T_2$ 可能正在并发运行甚至已经提交。
3. **Adya 的发现：** 一个环里至少得有两条 `rw` 边。如果只有 wr/ww，整个图就是时间顺流的，构不成环。
4. **Fekete 的发现 (关键)：** 这两条 `rw` 边必须是**相邻**的。
   * 假设环中有 $T_1 \xrightarrow{rw} T_2 \to \dots \to T_3 \xrightarrow{rw} T_1$。
   * 如果 $T_2$ 到 $T_3$ 之间全是 wr/ww 边，这意味着 $T_2$ 必须在 $T_3$ 之前提交。
   * 而 $T_1 \xrightarrow{rw} T_2$ 意味着 $T_1$ 和 $T_2$ 必须并发（或 $T_2$ 稍后）。
   * **结论：** 只有当 $T_2$ 既有一个入度 rw 边（被别人读了旧版本），又有一个出度 rw 边（读了别人的旧版本）时，才可能作为环的“枢纽”将时间线扭曲成环。

这个结构被称为 **Dangerous Structure**。

$$T_{in} \xrightarrow{rw} T_{pivot} \xrightarrow{rw} T_{out}$$

SSI 的算法本质：**在运行时检测这种“双 rw 边”结构，并 Abort 其中一个事务。**

## 3. PostgreSQL 的 SSI 实现架构

要在 PG 中实现 SSI，我们需要解决两个工程问题：如何检测读写冲突？如何管理内存？

### 3.1 全新的 SIREAD Lock Manager

PG 原有的 Lock Manager (Heavyweight) 和 Tuple Lock 都不适用，因为它们会阻塞。SSI 需要一种非阻塞的、仅用于追踪的锁。

我们在 `predicate.c` 中实现了 **SSI Lock Manager**。

* **SIREAD Locks:** 当事务读取数据时获取。
* **特点:** 不阻塞写，仅记录“$T_x$ 读取了 Tuple/Page/Relation $Y$”。
* **持久性:** 锁必须在事务提交后依然保留（因为 $T_{out}$ 可能还没结束）。

### 3.2 冲突检测机制 (RW-Conflict Detection)

检测分为两个方向，利用了 PG 现有的 MVCC 机制和新的锁表。

#### A. 检测 Write-before-Read (利用 MVCC)

场景：$T_{committed}$ 已经写了数据，$T_{current}$ 正在读。

* **机制：** 当 $T_{current}$ 扫描 Heap Tuple 时，通过可见性检查（`HeapTupleSatisfiesMVCC`）。
* **判定：** 如果发现 Tuple 的 `xmin` 是并发事务 $T_{committed}$ 且已提交，但在 $T_{current}$ 的快照中不可见 -> 说明 $T_{committed}$ 更新了数据但 $T_{current}$ 读了旧版本。
* **动作：** 记录 $T_{current} \xrightarrow{rw} T_{committed}$。
* **优势：** **零内存开销**，直接利用 Tuple Header 信息。

#### B. 检测 Read-before-Write (利用 SIREAD Locks)

场景：$T_{reader}$ 已经读了数据，$T_{writer}$ 想要修改。

* **机制：** 当 $T_{writer}$ 执行 `UPDATE/DELETE` 时，去 SSI Lock Manager 查询。
* **判定：** 检查谁持有该 Tuple/Page 的 SIREAD Lock。
* **动作：** 发现锁持有者 $T_{reader}$，记录 $T_{reader} \xrightarrow{rw} T_{writer}$。
* **注意：** 如果是索引扫描，会加索引页锁或 Relation 锁，以此来模拟 Predicate Locking（解决幻读）。

## 4. 挑战与解决方案

### 4.1 内存爆炸 (Bounded Memory)

SSI 需要追踪已提交事务的锁，这在长事务场景下极易撑爆共享内存。

* **Safe Snapshots:** (详见下文) 快速释放只读事务的锁。
* **粒度提升 (Granularity Promotion):** 如果一个 Page 上的 Tuple 锁太多，升级为 Page 锁；Page 锁太多，升级为 Relation 锁。这会增加假阳性（False Positives），但保证了内存有界。
* **Aggressive Cleanup:** 一旦确定某事务不可能参与到环中（例如所有并发事务都结束了），立即清理。
* **Summarization:** 对极老的已提交事务，将其压缩为摘要信息，只保留“是否有冲突”的标记。

### 4.2 假阳性与 Safe Retry

检测到危险结构 $T_1 \to T_2 \to T_3$ 不代表一定有环（可能 $T_3$ 在 $T_1$ 开始前就提交了，这就不是环）。

* **Commit Ordering 优化:** 只有当 $T_3$ 提交时间早于 $T_1$ 的快照时间时，才构不成环。我们利用这个规则减少 Abort 率。
* **Safe Retry:** 当必须 Abort 时，我们倾向于 Abort $T_2$ (Pivot)。因为 $T_2$ 重试时，原先的 $T_3$ 已经提交，新的依赖关系会变成 `wr` (可见读) 而不是 `rw`，从而打破死循环。

## 5. 针对只读事务的优化

只读事务在 SI 下也会读到异常数据（如 Report 生成），因此必须纳入 SSI 管理。但我们不想让它们承担太重开销。

### 5.1 Safe Snapshots (安全快照)

**理论：** 如果在只读事务 $T_{ro}$ 的生命周期内，没有任何并发读写事务提交了“指向旧事务的 rw 出边”，那么 $T_{ro}$ 是绝对安全的。

**实现：**

1. 只读事务启动时，记录当前所有并发的读写事务列表。
2. 当这些并发事务全部提交后，如果没有发现上述冲突，标记该快照为 **Safe**。
3. **收益：** Safe 的只读事务可以**丢弃所有 SIREAD Locks**，且后续读操作不再加锁。这极大减轻了锁表压力。

### 5.2 Deferrable Transactions

SQL

```
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE READ ONLY DEFERRABLE;
```

对于 `pg_dump` 这种超长只读事务，Abort 代价太高。

**逻辑：** 事务启动时不立即执行，而是 **Block**。直到系统确信当前快照已变为 Safe Snapshot 才放行。

**代价：** 启动延迟（通常几秒），换取运行时的绝对安全和零 SSI 开销。

## 6. 性能总结

根据 benchmark 数据：

* **读多写少 (Read-Heavy):** SSI 的性能损耗非常小（< 10%），TPS 远高于 S2PL。
* **写冲突激烈 (High Contention):** 性能会下降，因为 Abort 率上升。
* **CPU Overhead:** 主要来自 SSI Lock Manager 的维护和依赖图遍历，而非锁竞争。

## 7. 总结

PostgreSQL 的 SSI 实现是学术理论与工程实现的完美结合。它没有选择笨重的 S2PL，而是通过：

1. **精确的理论模型**（检测双 rw 边）。
2. **巧妙的工程妥协**（内存有界化、粒度提升）。
3. **针对性的优化**（Safe Snapshots）。

在保证严格串行化的同时，最大程度保留了 MVCC "读不阻塞写" 的核心优势。后续我们将结合代码 (`predicate.c`) 详细分析其锁清理机制。