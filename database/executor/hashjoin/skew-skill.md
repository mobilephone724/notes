
Thinking about a situation where plenty tuples (column) have the same hash value, it can cause the `hash join table` that
1. The first batch(in-memory) costs too much memory; or
2. One another batch contains too much tuples with means it takes us much IO to store and retrieve them.

