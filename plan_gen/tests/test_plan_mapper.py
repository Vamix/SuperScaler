import os
import json
from plan.node_list import NodeList
from plan.plan_mapper import GPURoundRobinMapper
from resources.resource_pool import ResourcePool


def test_gpu_round_robin():
    # Init mapper
    resource_yaml_path = os.path.join(
        os.path.dirname(__file__), 'data', 'resource_pool.yaml')
    rp = ResourcePool()
    rp.init_from_yaml(resource_yaml_path)
    mapper = GPURoundRobinMapper(rp)

    # Test map function
    path_input = os.path.join(os.path.dirname(__file__),
                              "data/test_generated_plan.json")
    node_list = json.load(open(path_input, 'r'))
    node_list = NodeList(node_list)

    mapped_node_list = mapper.map(node_list)
    path_output = os.path.join(os.path.dirname(__file__),
                               "data/test_mapped_plan.json")

    mappeded_node_list_ref = json.load(open(path_output, 'r'))
    assert(mapped_node_list.to_json() == mappeded_node_list_ref)

    # Wrong setup: Plan mapper with no-connection resources pool
    resource_yaml_no_connection = os.path.join(
        os.path.dirname(__file__), 'data', 'resource_pool_no_connection.yaml')
    rp_no_connection = ResourcePool()
    rp_no_connection.init_from_yaml(resource_yaml_no_connection)
    mapper_no_connection = GPURoundRobinMapper(rp_no_connection)

    assert(mapper_no_connection.map(node_list) is None)

    # None input
    mapped_node_list = mapper.map(None)
    assert(mapped_node_list is None)

    # Wrong input, assign 5 device into 4 GPUs resource_pool
    node_list = [
        {
            "device": "device_0",
            "name": "test",
            "op": "Allreduce",
            "output_shapes": [[1, 100]],
            "tensor_name": "test",
            "tensor_type": 1,
            "input": []
        },
        {
            "device": "device_1",
            "name": "test",
            "op": "Allreduce",
            "output_shapes": [[1, 100]],
            "tensor_name": "test",
            "tensor_type": 1,
            "input": []
        },
        {
            "device": "device_2",
            "name": "test",
            "op": "Allreduce",
            "output_shapes": [[1, 100]],
            "tensor_name": "test",
            "tensor_type": 1,
            "input": []
        },
        {
            "device": "device_3",
            "name": "test",
            "op": "Allreduce",
            "output_shapes": [[1, 100]],
            "tensor_name": "test",
            "tensor_type": 1,
            "input": []
        },
        {
            "device": "device_4",
            "name": "test",
            "op": "Allreduce",
            "output_shapes": [[1, 100]],
            "tensor_name": "test",
            "tensor_type": 1,
            "input": []
        },
    ]
    node_list = NodeList(node_list)
    mapped_node_list = mapper.map(node_list)
    assert(mapped_node_list is None)
