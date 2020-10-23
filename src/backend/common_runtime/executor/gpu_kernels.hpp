#pragma once

struct SumKernelGPUImpl
{
    template <class T>
    void operator()(const T* buffer, T* memory, size_t num_elements);
};

struct SynchronizedCopyKernelImpl {
    template <class T>
    void operator()(const T* buffer, T* memory, size_t num_elements);
};

struct ScaleKernelGPUImpl {
    template <class T>
    void operator()(T* memory, T scale, size_t num_elements);
};

struct DivKernelGPUImpl {
    template <class T>
    void operator()(T* memory, T scale, size_t num_elements);
};