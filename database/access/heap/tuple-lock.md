## heap_lock_tuple
### 1. deal with previous info

```
if (infomask & HEAP_XMAX_IS_MULTI) ### the tuple is being updated
    GetMultiXactIdMembers() #### who are locking the tuple?
    ## foreach member
        ## return if we got a heavier lock
        ## else ?
else if (TransactionIdIsCurrentTransactionId(xwait)) ### ?
```
#TODO: 

### 2. need sleep?
Since we haven't get the lock through the first step, we perhaps need sleep. But can we skip it?
> Initially assume that we will have to wait for the locking

