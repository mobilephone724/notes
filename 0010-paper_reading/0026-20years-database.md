# What happened in the last two decades

# 1 intro
RM(relational model) with an **extendable type system** has dominated all comers.

1. We structure our commentary into the following **areas**:
   1. MapReduce Systems
   2. Key-value Stores
   3. Document Databases
   4. Column Family/Wide-Column
   5. Text Search Engines
   6. Array Databases
   7. Vector Databases
   8. Graph Databases
2. Advancements in DBMS architectures that address **modern applications and hardware**
   1. Columnar Systems
   2. Cloud Databases
   3. Data Lakes/Lakehouses
   4. NewSQL Systems
   5. Hardware Accelerators
   6. Blockchain Databases


# 2 Data Models & Query Languages

## 2-1 MapReduce Systems(MR)
It is constructed as a "point solution" for processing its periodic crawl of the internet. In database terms, Map is a user-defined function (**UDF**) that performs computation and/or filtering while Reduce is a **GROUP BY operation**.

To a first approximation, MR runs a single query:

```
SELECT map() FROM crawl_table GROUP BY reduce()
```

* origin:
  * Google’s MR approach **did not prescribe a specific data model or query language**. Rather, it was up to the Map and Reduce functions written in a procedural MR program to parse and decipher the contents of data files.
  * Yahoo! developed an open-source version of MR in 2005, called **Hadoop**. It ran on top of a distributed file system **HDFS** that was a clone of the Google File System
* controversy between MR and DBMS
  * Google argued that with careful engineering, a MR system will beat DBMSs, and a user **does not have to load data with a schema before running queries on it**. Thus, MR is better for "one shot" tasks, such as text processing and ETL operations.
  * The DBMS community argued that MR incurs performance problems due to its design that existing parallel DBMSs already solved. (What's the performance problem?)
    * The use of higher-level languages (SQL) operating over **partitioned tables** would be better.
* **two changes** (BUT WHY?):
  * Many enterprises found that Hadoop has little interest and evelopers found it difficult to fit their applications.
  * Google announced that they were moving their crawl processing from MR to BigTable
    * Google needed to interactively update its crawl database in real time but MR was a batch system.
* end:
  * Cloudera rebranded(重命名) Hadoop to mean the whole stack (application, Hadoop, HDFS). In a further sleight-of-hand, Cloudera built a RDBMS, Impala, on top of HDFS but not using Hadoop.
  * Hadoop died about a decade ago,
  * At present, HDFS has lost its luster(光泽), as enterprises realize that there are better distributed storage alternatives
  * Meanwhile, distributed RDBMSs are thriving, especially in the cloud.

Some aspects of MR system implementations related to **scalability, elasticity, and fault tolerance** are carried over into **distributed RDBMSs**. MR also brought about the revival of shared-disk architectures with disaggregated storage, subsequently giving rise to open-source file formats and data lakes

## 2.2 Key/Value Stores

It represents the following binary relation:

```
(key,value)
```

It is up to the application to maintain the schema and parse the value into its corresponding parts. Most KV DBMSs only provide get/set/delete operations on a single value.

In the 2000s, several new Internet companies built their own shared-nothing, distributed KV stores for **narrowly focused applications**, like caching and storing session data. For caching:

* `Memcached` is the most well-known example of this approach.
  * [Memcached github page](https://github.com/memcached/memcached)
  * It seems like an old repo
* `Redis` markets itself as a Memcached replacement, offering a more robust query API with checkpointing support.
  * [Redis github page](https://github.com/redis/redis)
  * popular
* For more persistent application data, Amazon created the Dynamo KV store in 2007
  * [Amazon DynamoDB WebSite](https://aws.amazon.com/dynamodb/)
  * It seems not open.


Key/value stores provide a quick **"out-of-the-box"** way for developers to store data. If an application requires multiple fields in a record, then KV stores are probably a bad idea. Not only must the application parse record fields, but also there are no secondary indexes to retrieve other fields by value.

To deal with these issues, several systems began as a KV store and then morphed(变种) into a more feature-rich record store. Such systems replace the opaque value with a **semi-structured** value, such as a JSON document.

One new architecture trend from the last 20 years is **using embedded KV stores as the underlying storage manager for full-featured DBMSs**:
* MySQL was the first DBMS to **expose an API** that allowed developers to replace its default KV storage manager.
* This API enabled Meta to build RocksDB to replace InnoDB for its massive fleet of MySQL databases.
* Similarly, MongoDB discarded their ill-fated MMAP-based storage manager in favor of WiredTiger’s KV store in 2014

## 2.3 Document Databases

The document data model represents a database as a **collection of record objects**. Each document contains a hierarchy of field/value pairs, where each field is identified by a name and a field’s value can be either a scalar type, an array of values, or another document.

An json example:

```json
{ "name": "First Last",
  "orders": [ { "id": 123, "items": [...] },
              { "id": 456, "items": [...] }, ] }
```

This has given rise to data formats like **SGML** and **XML**, and **json** becomes the standard in web-based applications

There were two marketing messages for such systems that resonated(共鸣) with developers.

1. SQL and joins are slow, and one should use a "faster" lower-level, record-at-a- time interface.
2. ACID transactions are unnecessary for modern applications, so the DBMS should only provide weaker notion of it

There are dozens of such systems, of which [MongoDB](https://github.com/mongodb/mongo) is the most popular.

two benefits for Document DBMSs or object-oriented DBMSs
1. Storing data as documents removes the impedance mismatch between **how application OO code interacts with data** and **how relational databases store them**.
2. Denormalizing entries into nested structures is better for performance because it **removes the need to dispatch multiple queries to retrieve data related to a given object**

The problems with denormalization/prejoining is an old topic that dates back to the 1970s
1. If the join is not one-to-many, then there will be duplicated data
2. prejoins are not necessarily faster than joins
3. there is no data independence


Adding SQL and ACID to a NoSQL DBMS lowers their intellectual distance from RDBMSs. The **main differences** between them seems to be JSON support and the fact that NoSQL vendors allow "schema later" databases. But the SQL standard added a **JSON data type** and operations in 2016 [165, 178]. And as RDBMSs continue to improve their "first five minutes" experience for developers, we believe that the two kinds of systems will soon be effectively identical.

## 2.4 Column-Family Databases
It is a reduction of the document data model that only supports **one level of nesting** instead of arbitrary nesting; it is relation-like, but each record can have optional attributes, and cells can contain an array of values.
```
User1000 → { "name": "Alice", "accounts": [ 123, 456 ],
             "email": "xxx@xxx.edu" }
User1001 → { "name": "Bob",
             "email": [ "yyy@yyy.org", "zzz@zzz.com" ]
```

## 2.5 Text Search Engines
* Text search engines, by **tokenizing documents** into a “bag of words” and then **building full-text indexes**, on those tokens to support queries on their contents.
* The leading text search systems today include **Elastic-search** and **Solr** , which both use **Lucene** as their internal search library.
  * https://github.com/elastic/elasticsearch
  * https://github.com/apache/solr
  * https://github.com/apache/lucene
* These systems offer **good support for storing and indexing text data** but offer **none-to-limited transaction capabilities**.
* All the leading RDBMSs support full-text search indexes, including **Oracle**, **Microsoft SQL Server**, **MySQL** , and **PostgreSQL**.
* Text data is **inherently unstructured**, bug a DBMS seeks to **extract structure** (i.e., meta-data, indexes) from text to avoid “needle in the haystack” sequential searches.
* Three ways to manage text data in application:
  * (1): one can run multiple systems, such as Elastic- search for text and a RDBMS for operational workloads. This approach:
    * Allows one to run **"best of breed"** systems
    * but requires additional ETL(Extract, transform, and load) plumbing to push data from the operational DBMS to the text DBMS
    * rewrite applications to **route queries to the right DBMSs** based on their needs.
  * (2): one can run a RDBMS with good text-search integration capabilities but with divergent APIs in SQL. This issue is often overcome by application frameworks that hide this complexity
  * (3): use a **polystore system** [Home | bigdawg (mit.edu)](https://bigdawg.mit.edu/) that masks the system differences via middleware that exposes a unified interface


## 2.6 Array Databases
We use the term “array” to mean all variants of **vectors**, **matrices** and tensors (**three** or more dimensions). For example, scientific surveys for geographic regions usually represent data as a multi-dimensional array that stores sensor measurements using location/time-based coordinates:
```
(latitude, longitude, time, [vector-of-values])
```

Array data does **not always align** to a regular integer grid, for example, **geospatial** data is often split into irregular shapes. An application can map such grids to integer coordinates **via metadata describing this mapping**. Hence, most applications maintain array and non-array data together in a single database.

Querying array data in arbitrary dimensions presents unique challenges, since the DBMS stores **multi-dimensional** array data on a **linear physical storage** medium like a disk.

## 2.7 Vector Databases
Store **single-dimension embeddings generated from AI tools.**

For example, one could convert each Wikipedia article into an embedding using Google **BERT** and store them in a vector database along with additional article meta-data:

```
(title, date, author, [embedding-vector])
```

The key difference between vector and array DBMSs is their **query patterns**. Vector DBMS are designed for **similarity searches** that find records whose vectors have the shortest distance to a given input vector in a high-dimensional space. Unlike array DBMSs, applications do not use vector DBMSs to search for matches at an offset in a vector nor extract slices across multiple vectors.

Vector DBMSs build indexes to accelerate **approximate nearest neighbor** (ANN) searches . One compelling feature of vector DBMSs is that they provide **better integration with AI tools**: These systems natively support **transforming a record’s data into an embedding upon insertion** using these tools and then uses the same transformation to convert a query’s input arguments into an embedding to perform the ANN search;

There are two likely explanations for the quick proliferation(扩散) of vector indexes:
1. Similarity search via embeddings is such a compelling use case that every DBMS vendor rushed out their version and announced it immediately
2. The engineering effort to introduce a new index data structure

## 2.8 Graph Databases

- Many applications use knowledge graphs to model **semi-structured information**
- Social media applications inherently contain **graph-oriented relationships** (“likes”, “friend-of”).

Relational design tools provide users with an entity-relationship (**ER**) model of their database. **An ER diagram is a graph**; thus, this paradigm has clear use cases.

The two most prevalent approaches to represent graphs are
1. the resource description framework (RDF) (aka triplestores)
    1. model a directed graph with labeled edges
2. property graphs:
    1. DBMS maintains a directed multi-graph structure that supports **key/value labels for nodes and edges**.

usages:
- operational / OLTP workloads:
    - traditional DBMS: adds a friend link in the database by **updating a single record**, presumably in a transactional manner
    - [Neo4j](https://github.com/neo4j/neo4j) is the most popular graph DBMS for OLTP applications. It supports edges using pointers (as in [CODASYL](https://en.wikipedia.org/wiki/CODASYL) ) but it does not cluster nodes with their “parent” or “offspring”
        - Such an architecture is advantageous for **traversing long edge chains** since it will do **pointer chasing**, whereas a RDBMS has to do this via joins.
- analytics: which seeks to derive information from the graph.
    - finding which user has the most friends under 30 years old.

Unlike queries in relational analytics that are characterized by chains of joins, queries for graph analytics contain operations like **shortest path**, **cut set**, or [clique determination](https://en.wikipedia.org/wiki/Clique_problem) . This argues for a computing fabric that allows developers to write their own algorithms using an abstraction that hides the underlying system topology.

Regardless of whether a graph DBMS targets OLTP or OLAP workloads, the key challenge these systems have to overcome is that it is possible to simulate a graph as a collection of tables:
```
Node (node_id, node_data)
Edge (node_id_1, node_id_2, edge_data)
```
This means that RDBMSs are always an option to support graphs. But “vanilla” SQL is not expressive enough for graph queries and thus require multiple client-server roundtrips for traversal operations.

Some RDBMSs, including MSSQL and Oracle, provide built-in SQL extensions that make storing and querying graph data easier. Other DBMSs use a transla- tion layer on top of relations to support graph-oriented APIs.

More recently, **SQL:2023 introduced property graph queries (SQL/PGQ) for defining and traversing graphs in a RDBMS** 

There have been several performance studies showing that graph simulation on RDBMSs outperform graph DBMSs. More recent work showed how SQL/PGQ in DuckDB outperforms a leading graph DBMS by up to 10.

## 2.9 Summary
- **MapReduce Systems**: They died years ago and are, at best, a legacy technology at present.
- **Key-value Stores**: Many have either matured into RM systems or are only used for specific problems. These can generally be equaled or beaten by modern high-performance RDBMSs.
- **Document Databases**: Such NoSQL systems are on a **collision course** with RDBMSs. The differences between the two kinds of systems have diminished over time and should become **nearly indistinguishable** in the future.
- **Column-Family Systems**: These remain a niche market. Without Google, this paper would not be talking about this category.
- **Text Search Engines**: These systems are used for text fields in a polystore architecture.
- **Array Databases** : Scientific applications will continue to ignore RDBMSs in favor of bespoke(定制) array systems
- **Vector Databases** : They are single-purpose DBMSs with indexes to accelerate nearest-neighbor search. RM DBMSs should soon provide native support for these data structures and search methods using their extendable type system that will render such specialized databases unnecessary.
- **Graph Databases**: OLTP graph applications will be largely served by RDBMSs. In addition, analytic graph applications have unique requirements that are best done in main memory with specialized data structures. RDBMSs will **provide graph-centric APIs** on top of SQL or via extensions. We do not expect specialized graph DBMSs to be a large market.

# 3 system Architectures

## 3.1 Columnar Systems

Data warehouse (OLAP) applications have common properties that are distinct from OLTP workloads:
1. They are historical in nature
2. Organizations retain everything as long as they can afford the storage — think terabytes to petabytes.
3. Queries typically only access a small subset of attributes from tables and are ad-hoc in nature.

Organizing the DBMS’s storage by columns instead of rows has several benefits
1. **Compressing** columnar data is more effective than row-based data because there is a single value type in a data block often many repeated bytes.
2. A Volcano-style engine executes operators once per row. In contrast, a column-oriented engine has an inner loop that **processes a whole column using vectorized instructions**
3. Row stores have a large header for each record (e.g., 20 bytes) to track nulls and versioning meta-data, whereas column stores have **minimal storage overhead per record**.

## 3.2 Cloud Databases

Initial cloud DBMS offerings repackaged on-prem systems into managed VMs **with direct-attached storage**. But over the last 20 years, **networking bandwidth** has increased much faster than disk bandwidth, making network attached storage (**NAS**) attractive as an alternative to attached storage. This has caused a profound rethinking of DBMS architectures for the cloud.

All major cloud vendors offer NAS via object stores. Beyond better economics compared to direct-attached storage, object stores have **several advantages that compensate for the cost of the added network link**
1. because the compute nodes are disconnected from the storage nodes, a system can provide per-query **elasticity**;
    1. The DBMS can **add new compute nodes dynamically** without having to reshuffle(重新组织) data.
    2. It also allows the DBMS to use **different hardware for its storage nodes** than compute nodes.
2. the system can **reassign compute nodes to other tasks** if a DBMS is underutilized.
3. On the other hand, in a shared-nothing DBMS, a node must always be online to handle incoming query requests.
4. **Pushing down computation into the storage nodes** is possible

https://www.snowflake.com/en/

From a business perspective, open-source DBMSs face the danger of becoming too popular and being monetized by the major cloud providers.

## Data Lakes / Lakehouses

From monolithic(单机的), dedicated(专用的) data warehouses for OLAP workloads and towards data lakes backed by object stores. Vendors viewed their DBMSs as the **“gatekeepers”** for all things related to data in an organization.

With a data lake architecture, applications **upload files to a distributed object store**, bypassing the traditional route through the DBMS. Users then **execute queries** and processing pipelines **on these accumulated files using a** *lakehouse* (a portmanteau(多用途的) of data warehouse and data lake) execution engine

Instead of using DBMS-specific proprietary file formats or inefficient text-based files (e.g., CSV, JSON), applications write data to data lakes using open-source, disk-resident file formats. The two most popular formats are Twitter/Cloudera’s **[Parquet](https://parquet.apache.org/)** and Meta’s **[ORC]([Background (apache.org)](https://orc.apache.org/docs/))**

At first glance, a data lake seems like a terrible idea for an organization: **allowing any application to write arbitrary files into a centralized repository without any governance is a recipe for integrity, discovery, and versioning problems**

Data lakes introduce new challenges to query optimization. DBMSs have always struggled with acquiring **precise statistics** on data, leading to poor query plan choices [154]. However, a data lake system **may completely lack statistics on newly ingested data files**.

All the major cloud vendors now offer some variation of a managed data lake service. Since **data lake systems backed by object stores are much cheaper per gigabyte than proprietary data warehouses**, the legacy OLAP vendors (e.g., Teradata, Vertica) have extended their DBMSs to support reading data from object stores in re- sponse to this pricing pressure.

## 3.4 NewSQL Systems

NewSQL systems arrived in the early 2010s seeking to provide the **scalability of NoSQL** systems for **OLTP workloads while still supporting SQL**.

There were two main groups of NewSQL systems:
1. in-memory DBMSs, including [H-Store](https://github.com/apavlo/h-store), [SingleStore](https://www.singlestore.com/), Hekaton, HyPer
2. disk-oriented, distributed DBMSs like NuoDB and Clustrix

There has yet to be a dramatic uptake in NewSQL DBMS adoption. The reason for this lackluster(乏善足陈) interest is that existing DBMSs were good enough for the time, which means organizations are unwilling to take on the costs and risk of migrating existing applications to newer technologies.

The aftermath of NewSQL is a new crop(收成) of distributed, transactional SQL RDBMSs. These include TiDB, CockroachDB, and YugabyteDB.

The major NoSQL vendors also added transactions to their systems in the last decade despite previously strong claims that they were unnecessary.

## 3.5 Hardware Accelerators

specialized hardware designed for a DBMS should easily outperform a conventional CPU.

Instead of building custom hardware for DBMSs, the last 20 years have been about **using commodity(商品) hardware (FPGAs, GPUs) to accelerate queries**.This is an enticing(有新引力的) idea: a vendor can get the benefits of a DBMS accelerator without the cost of fabricating the hardware

Creating custom hardware just for a DBMS is **not cost-effective** for most companies. The reason why there are more GPU DBMSs than FPGA systems is because there are existing support libraries available for GPUs.

The only place that custom hardware accelerators will succeed is for the large cloud vendors. They can justify the $50–100m R&D(research and development) cost of custom hardware at their massive scale. Amazon did this already with their Redshift AQUA accelerators. Google BigQuery has custom components for in-memory shuffles.

## 3.6 Blockchain Databases

These are decentralized log-structured databases (i.e., ledger) that maintain **incremental checksums** using some variation of [Merkle trees](https://en.wikipedia.org/wiki/Merkle_tree). These incremental checksums are how a blockchain ensures that the database’s log records are immutable: **applications use these checksums to verify that previous database updates have not been altered**.

The ideal use case for blockchain databases is peer-to-peer applications where one cannot trust anybody. There is no centralized authority that controls the ordering of updates to the database. Thus, blockchain implementations use a BFT(Byzantine Fault Tolerant) commit protocol to determine which transaction to apply to the database next.

At the present time, cryptocurrencies (Bitcoin) are **the only use** case for blockchains. In addition, there have been attempts to build a usable DBMS on top of blockchains.

We are required to place trust in several entities in today’s society. When one sells a house, they trust the title company to manage the transaction. **The only applications without real-world trust are dark web interactions**. Legitimate businesses are unwilling to pay the performance price (about five orders of magnitude(数量级)) to use a blockchain DBMS. If organizations trust each other, they can run a shared distributed DBMS more efficiently without wasting time with blockchains.

Blockchain proponents make additional meaningless claims of achieving data resiliency through replication in a peer-to-peer environment. No sensible company would rely on random participants on the Internet as the backup solution for mission-critical databases.

## 3.7 Summary
- **Columnar Systems**: The change to columnar storage revolutionized OLAP DBMS architectures.
- **Cloud Databases**: The cloud has upended(颠覆) the conventional wisdom on how to build scalable DBMSs.
- **Data Lakes / Lakehouses**: Cloud-based object storage using open-source formats will be the OLAP DBMS archetype for the next ten years.
- **NewSQL Systems**: They leverage new ideas but have yet to have the same impact as columnar and cloud DBMSs.  It has led to new distributed DBMSs that support stronger ACID semantics as a counter to NoSQL’s weaker BASE guarantees.
- **Hardware Accelerators**: We do not see a use case for specialized hardware outside of the major cloud vendors, though start-ups will continue to try.
- **Blockchain Databases**: An inefficient technology looking for an application. History has shown this is the wrong way to approach systems development.

## 4 Parting Comments

- **Never underestimate the value of good marketing for bad products**. Inferior DBMS products have succeeded via strong marketing despite the existence of better options available at the time:
    - **Oracle** did this in the 1980s,
    - **MySQL** did this in the 2000s, and
    - **MongoDB** did this in the 2010s. 
    - These systems got enough traction early on to buy them time to fix the engineering debt they accumulated earlier.
- **Beware of DBMSs from large non-DBMS vendors**
    - This trend to avoid “**not invented here**” software is partly because many companies’ promotion path favors engineers who make new internal systems, even if existing tools are sufficient.
- **Do not ignore the out-of-box experience**
    - Most SQL systems **require one first to create a database and then define their tables before they can load data**. This is why data scientists use **Python notebooks** to analyze data files quickly. Every DBMS should, therefore, **make it easy to perform in situ processing of local and cloud-storage files**. DuckDB’s rising popularity is partly due to its ability to do this well.
- **Developers need to query their database directly.**
    - Most OLTP applications created in the last 20 years primarily **interact with databases via an abstraction layer, such as an endpoint API**
    - ORMs(object-relational mapper) are a vital tool for rapid prototyping. But they often **sacrifice the ability to push logic into the DBMS** in exchange for interoperability with multiple DBMSs.
- The impact of AI/ML on DBMSs will be significant.
    - There is a resurgence in using natural languages (NLs) to query databases due to advancements in LLMs at converting NL to query code
    - Nobody will write OLTP applications using an NL, as most generate queries using ORMs. For OLAP databases, NL could prove helpful in constructing the initial queries for exploratory(探索性的) analysis. However, these queries should be exposed to a dashboard-like refinement tool since English and other NLs are rife with ambiguities and impreciseness.
    - Lastly, there is a considerable amount of recent research on using AI/ML to optimize the DBMSs. Although such ML-assisted optimizations are powerful tools to improve the performance of DBMSs, it does not obviate the need for high-quality systems engineering.

# 5 Conclusion

- There is tremendous value in exploring new ideas and concepts for DBMSs. The database re- search community and marketplace are more robust be- cause of it. However, we do not expect these new data models to supplant the RM.
- We contend that the database community should strive for a POSIX-like standard of DBMS internals to accelerate interoperability.

# Related Paper
* [amazon-dynamo-sosp2007](../assets/0026-002-amazon-dynamo-sosp2007.pdf)
* [whatgoesaround-sigmodrec2024](../assets/0026-001-whatgoesaround-sigmodrec2024.pdf)

