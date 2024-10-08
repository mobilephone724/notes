---
title: "cublasDgemm"
author: "mobilephone724"
math: true
---
## concept
`cublasDgemm` is a convenient function in cublas to compute the product of two matrix, while letter 'D' in `cublasDgemm` means `double`.

Before reading this post, basic cuda functions like `cudaMalloc` are what you are supposed to know.
## basic use
Definition of this function
```c++
cublasStatus_t cublasDgemm(cublasHandle_t handle,
                           cublasOperation_t transa, cublasOperation_t transb,
                           int m, int n, int k,
                           const double *alpha,
                           const double *A, int lda,
                           const double *B, int ldb,
                           const double *beta,
                           double *C, int ldc)
```
[Basic information of parameters is show in this page](https://docs.nvidia.com/cuda/cublas/index.html). Simply put, $C = \alpha A \times B + \beta C $ .But it may remains confused for fresher. Below is an simple example.
```c++
/* A is matrix in gpu memory looks like
 * 1 2 3
 * 4 5 6
 * 7 8 9
 * and ptr_A is a pointer to A
 *
 * B is matrix in gpu memory looks like
 * 1 2
 * 3 4
 * 5 6
 * and ptr_A is a pointer to A
 *
 * While memory is one-dimensional while matrix is two-dimensional, I 
 * suggeset that all matrix in gpu memory are stored in column major for 
 * convevient use of cublas. In this case, A in memory is like 
 * [1, 4, 7, 2, 5, 8, 3, 6, 9].
 * C is a matrix to store the product of A * B
 */

//get handle and stat of this function
cublasHandle_t handle;
cublasStatus_t stat = cublasCreate(&handle);
if (stat != CUBLAS_STATUS_SUCCESS)
{
	printf("CUBLAS initialization failed\n");
	return EXIT_FAILURE;
}
//setting alpha and cuda
double alpha = 1.0, beta = 0.0;
stat = cublasDgemm(	handle, 
					CUBLAS_OP_N,	// we use matrix A instead of A^T
					CUBLAS_OP_N,	// we use matrix B instead of B^T
					3,				// the row of A 
					2,				// the col of B
					3,				// the row of B(ro col of A)
					&alpha,
					devPtrA,
					3,				// the leading dimension of A
					devPtrB,
					3,				// the leading dimension of B
					&beta,
					devPtrC,
					3);				// the leading dimension of C
/*
 * if we want to compute C = A^T * B
 */
stat = cublasDgemm(	handle, 
					CUBLAS_OP_T,	// we use matrix A^T instead of A
					CUBLAS_OP_N,	// we use matrix A instead of B^T
					3,				// the row of A^T
					2,				// the col of B
					3,				// the row of B(or col of A^T)
					&alpha,
					devPtrA,
					3,				// the leading dimension of A^T. 
									// So whether or not A or A^T, the leading dimension 
									// of A or A^T is the row of A, decided when A is 
									// initialized in memory
					devPtrB,
					3,				// the leading dimension of B
					&beta,
					devPtrC,
					3);				// the leading dimension of C
if (stat != CUBLAS_STATUS_SUCCESS)
{
	printf("cublasSgemm failed\n");
	return EXIT_FAILURE;
}
```
An obvious question is what is `leading dimension` for we have know the column and row of A and B, no more information is need to finish this computation.

My understanding of leading dimension is the `offest` to get the element in next column at the same row. An implement to compute the product of submatrix. below is an example. `A` and `B` are the same matrix in the previous example.

And what we want to compute is $A[0:1][0:1] \times B[1:2][0:1]$.
```c++
stat = cublasDgemm(	handle, 
					CUBLAS_OP_N,	// we use matrix A[0:1][0:1] instead of A[0:1][0:1]^T
					CUBLAS_OP_N,	// we use matrix B[1:2][0:1] instead of B[1:2][0:1]^T
					2,				// the row of A[0:1][0:1]
					2,				// the col of B[1:2][0:1]
					2,				// the row of A[0:1][0:1](or col of B[1:2][0:1])
					&alpha,
					devPtrA,		// pointer to A[0][0]
					3,				// the offset of A[0][0] to A[0][1] is 3 of double size
					devPtrB + 1,	// pointer to B[1][0]
					3,				// the offset of B[1][0] to B[1][1] is 3 of double size
					&beta,
					devPtrC,
					2);				// the leading dimension of C
```
So it's the use of leading dimension which makes matrix production more flexible
