#pragma once

#ifdef GPU_SWITCH

#include <cstdio>
#include <unistd.h>
#include <stdint.h>
#include <stdlib.h>
#include <cuda_runtime.h>
#include <chrono>
#include <stdio.h>
#include <iostream>
#include <cmath>

#define BLOCK 512

inline dim3 cuda_gridsize_1d(int n){
    int x = (n-1) / BLOCK + 1;
    dim3 d = {(uint) x, 1, 1};
    return d;
}

template <class T>
__global__ static void SumKernel(const T* buffer, T* memory, size_t num_elements)
{
    int index = blockIdx.x*blockDim.x + threadIdx.x;
    if (index >= num_elements) return;
    memory[index] += buffer[index];
}

struct SumKernelGPUImpl {
    template <class T>
    void operator()(const T* buffer, T* memory, size_t num_elements) {
        SumKernel<T><<<cuda_gridsize_1d(num_elements), BLOCK, 0, 0>>>(buffer, memory, num_elements);
    }
};

struct SynchronizedCopyKernelImpl {
    template <class T>
    void operator()(const T* buffer, T* memory, size_t num_elements) {
        cudaMemcpy(memory, buffer, num_elements * sizeof(T), cudaMemcpyDeviceToDevice);
    }
};

template <class T>
__global__ static void ScaleKernel(T* memory, T scale, size_t num_elements)
{
    int index = blockIdx.x*blockDim.x + threadIdx.x;
    if (index >= num_elements) return;
    memory[index] = memory[index] * scale;
}

struct ScaleKernelGPUImpl {
    template <class T>
    void operator()(T* memory, T scale, size_t num_elements) {
        ScaleKernel<T><<<cuda_gridsize_1d(num_elements), BLOCK, 0, 0>>>(memory, scale, num_elements);
    }
};

template <class T>
__global__ static void DivKernel(T* memory, T scale, size_t num_elements)
{
    int index = blockIdx.x*blockDim.x + threadIdx.x;
    if (index >= num_elements) return;
    memory[index] = memory[index] / scale;
}

struct DivKernelGPUImpl {
    template <class T>
    void operator()(T* memory, T scale, size_t num_elements) {
        DivKernel<T><<<cuda_gridsize_1d(num_elements), BLOCK, 0, 0>>>(memory, scale, num_elements);
    }
};

#endif