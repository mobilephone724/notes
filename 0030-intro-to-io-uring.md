# Introduction To IO_URING
## Related blogs

- [https://cloud.tencent.com/developer/article/2187655](https://cloud.tencent.com/developer/article/2187655)
- [io_uring by example: Part 1 – Introduction – Unixism](https://unixism.net/2020/04/io-uring-by-example-part-1-introduction/)

## Intro From chatgpt

**io_uring** is a Linux kernel feature introduced in version 5.1, designed to improve the performance and efficiency of asynchronous I/O operations. It aims to reduce the overhead associated with I/O system calls like read(), write(), and poll() by **minimizing the number of context switches between user space and kernel space**, which traditional I/O mechanisms (e.g., epoll and aio) suffer from. Here’s a breakdown of how **io_uring** works and its key features:

### **1. How io_uring Works**

At its core, io_uring is based on two ring buffers: a submission queue (SQ) and a completion queue (CQ). These queues are shared between user space and the kernel, allowing efficient communication without frequent system calls. Here’s how it operates:

- **Submission Queue (SQ):** This is where user space places I/O requests (such as reads or writes) that it wants the kernel to execute.
- **Completion Queue (CQ):** After the kernel processes an I/O request, it places the result in this queue, where user space can check for completion.

By sharing these queues between user space and the kernel, io_uring reduces the need for expensive system calls (such as epoll_wait()), as requests and completions can be submitted and polled in batches.

### **2. Key Features of io_uring**

- **Low Latency:** By minimizing context switches and avoiding the need to make multiple system calls for each operation, io_uring reduces I/O latency significantly compared to older asynchronous I/O methods.
- **High Throughput:** io_uring is designed to handle a large number of concurrent I/O requests efficiently, making it ideal for applications with high I/O workloads, such as databases, web servers, and high-performance networking services.
- **Kernel Bypass:** Instead of relying on system calls for every I/O request, user space can submit requests directly to the kernel through the submission queue, thus bypassing the traditional syscall overhead.
- **Multishot Requests:** io_uring supports multishot operations, allowing user space to issue a single request that results in multiple completions (e.g., for accept() or recv()), reducing the need to resubmit similar operations.
- **Zero-Copy Support:** io_uring supports zero-copy networking, reducing the overhead of copying data between user space and kernel space during network I/O operations.

### **3. Use Cases**

- **High-performance Networking:** io_uring is a good fit for applications like web servers and proxy servers that handle a large number of concurrent network connections and need efficient I/O.
- **Databases:** Databases can leverage io_uring to improve the performance of disk I/O operations, especially in environments where I/O performance is a bottleneck.
- **File I/O in High-throughput Systems:** File servers or systems requiring a high rate of disk operations, such as video streaming services, can use io_uring to optimize large-scale reads and writes.

### **4. Advantages over Previous Methods**

- **Compared to** epoll io_uring provides a more efficient mechanism for handling asynchronous I/O compared to epoll. With epoll, a system call is required for each I/O operation, leading to higher context switching overhead.
- **Compared to** aio The traditional Linux asynchronous I/O (AIO) API is more limited and has some issues with performance and ease of use. io_uring offers a better interface and improved performance, especially for disk I/O.

### 5. Example

```c
/*
 * sudo apt install liburing-dev
 * gcc test.c -luring
 */

#include <liburing.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

int main() {
    struct io_uring ring;
    struct io_uring_sqe *sqe;
    struct io_uring_cqe *cqe;
    char buffer[4096];
    
    int fd = open("testfile.txt", O_RDONLY);
    
    // Initialize io_uring
    io_uring_queue_init(8, &ring, 0);
    
    // Get the submission queue entry
    sqe = io_uring_get_sqe(&ring);
    
    // Prepare a read operation
    io_uring_prep_read(sqe, fd, buffer, sizeof(buffer), 0);
    
    // Submit the I/O request
    io_uring_submit(&ring);
    
    // Wait for the completion
    io_uring_wait_cqe(&ring, &cqe);
    
    // Check result
    if (cqe->res > 0) {
        write(1, buffer, cqe->res); // Write to stdout
    }
    
    // Mark completion as seen
    io_uring_cqe_seen(&ring, cqe);
    
    // Clean up
    close(fd);
    io_uring_queue_exit(&ring);
    
    return 0;
}
```

## How does linux kernel know the request in SQ

The Linux kernel knows that there is a new request in the **Submission Queue (SQ)** of **io_uring** through a combination of techniques

### **1. Polling/Batching (Without Immediate Notification).**

In this mode, the kernel checks the submission queue periodically, often in conjunction with other kernel operations.

1. **Polling Loop:** The kernel, while executing other I/O or task scheduling, can periodically check the submission queue for new requests.
2. **Batch Submission**: User-space applications can also batch multiple I/O operations before invoking a system call (`io_uring_submit()`) to notify the kernel that there are new requests to process.

### **2. System Call Notification (`io_uring_enter()`)**

making a system call, specifically `io_uring_enter()` [man page](https://man7.org/linux/man-pages/man2/io_uring_enter.2.html)

```c
#include <liburing.h>
int io_uring_enter(unsigned int fd, unsigned int to_submit,
                   unsigned int min_complete, unsigned int flags,
                   sigset_t *sig);
int io_uring_enter2(unsigned int fd, unsigned int to_submit,
                    unsigned int min_complete, unsigned int flags,
                    sigset_t *sig, size_t sz);
```

When the system call is made, the kernel starts processing the requests placed in the submission queue by the user space.

### 3. **Submission Queue Polling (Kernel-side Polling)**

In high-performance environments, where the application requires extremely low latency, **submission queue polling** can be enabled. This feature allows the kernel to continuously poll the submission queue for new I/O requests without requiring the user space to make a system call. This mode is often used for applications that need to minimize latency and can afford the CPU overhead of polling.

**SQPOLL Mode:** In this mode, the kernel spawns a kernel thread that continuously polls the submission queue for new requests. This eliminates the need for system calls and greatly reduces the latency for request submissions, making it suitable for real-time or high-frequency I/O operations.

1. To use SQPOLL mode, the user needs to set the `IORING_SETUP_SQPOLL` flag during `io_uring_setup()`, which enables kernel-side polling of the submission queue.
2. This mode has the advantage of minimizing user-to-kernel transitions, but it can be CPU-intensive because the kernel is constantly polling for new requests.