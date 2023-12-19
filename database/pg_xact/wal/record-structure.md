Logically, a `WAL` record must contains the three parts below:
1. Which page to modify.(An unique ID, See [block](../../storage/block.md) and [relfilelocator](../../storage/relfilelocator.md) for detail)
2. The kind of `WAL`. Different kinds of `WAL` have different modification methods
3. The way to modify the page

## Unique page ID
For heap pages:
* A `relfilelocator` + `block number` can locate to a concrete page
* But structure `registered_buffer` also add `ForkNumber` here
    * Record the changes of `fsm` and `vm`
    * See [insert](insert.md) for how the unique id is record