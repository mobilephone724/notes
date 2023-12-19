## buffer tag
```C
BufferGetTag(Buffer buffer, RelFileLocator *rlocator, ForkNumber *forknum,
             BlockNumber *blknum)
{
    bufHdr = GetLocalBufferDescriptor/GetBufferDescriptor
    *rlocator = BufTagGetRelFileLocator(&bufHdr->tag);
    *forknum = BufTagGetForkNum(&bufHdr->tag);
    *blknum = bufHdr->tag.blockNum;
}
```
