---
title: "Column Schema Change"
date: 2024-04-07T22:19:24+08:00
---

In PostgreSQL, the adding and dropping a column is an instant ddl(This name seems only to be used in mysql, but I like it). In this article, I try to explain the implement of that.

**The reference:**

* https://www.postgresql.org/docs/current/sql-altertable.html
* 

## Basic Concepts


### instant ddl

For a table with $n$ tuples, if a ddl post can be performed in time $O(1)$ ,we call this ddl instant. So to implement an instant ddl, the data organization must remain unchanged. Instead, only the schema information can be changed, along withthe method to used to interpret the table's binary data according to the schema.

In this scenario, pg only changes the `pg_attribute` catalog, which records the attributes[#todo is this OK] of each relations.



### heap page representation


Before illustrate the situation where interpreting the binary data with two different schemas, we figure out the way to organize the heap pages.



![image-20240407223441847](https://raw.githubusercontent.com/mobilephone724/blog_pictures/master/image-20240407223441847.2024_04_07_1712500481.png)

