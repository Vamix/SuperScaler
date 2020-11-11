import os
import json
import pytest
import subprocess
from frontend.scaler_graph import DataParallelism
from frontend.tests.data import dummy_model
import frontend.tensorflow as superscaler
from frontend.superscaler import SuperscalerError


def is_gpu_available():
    """
        Check NVIDIA with nvidia-smi command
        Returning code == 0 and count > 0, it means NVIDIA is installed
        and GPU is available for running
        Other means not installed
    """
    code = os.system('nvidia-smi')
    if code == 0:
        cmd = "nvidia-smi --query-gpu=name --format=csv,noheader | wc -l"
        count = subprocess.check_output(cmd, shell=True)
        return int(count) > 0
    else:
        return False


def test_superscaler_tf():

    # Create Superscaler_TF class
    sc = superscaler()

    # Init parameters
    apply_gradient_op, loss = dummy_model.SimpleCNN()
    strategy = DataParallelism(range(2))
    deployment_setting = {"1": "10.0.0.25"}
    communication_DSL = "ring"
    resource_pool = os.path.join(
        os.path.dirname(__file__), 'data', 'resource_pool.yaml')

    if is_gpu_available():
        # Check for wrong input
        with pytest.raises(SuperscalerError):
            # Wrong apply_gradient_op
            sc.init(None, loss, deployment_setting, strategy,
                    communication_DSL, resource_pool)
        with pytest.raises(SuperscalerError):
            # Wrong loss
            sc.init(apply_gradient_op, None, deployment_setting, strategy,
                    communication_DSL, resource_pool)
        with pytest.raises(SuperscalerError):
            # Wrong deployment_setting
            sc.init(apply_gradient_op, loss, None, strategy,
                    communication_DSL, resource_pool)
        with pytest.raises(SuperscalerError):
            # Wrong strategy
            sc.init(apply_gradient_op, loss, deployment_setting, None,
                    communication_DSL, resource_pool)
        with pytest.raises(SuperscalerError):
            # Wrong communication_DSL
            sc.init(apply_gradient_op, loss, deployment_setting, strategy,
                    None, resource_pool)
        with pytest.raises(SuperscalerError):
            # Wrong resource_pool
            sc.init(apply_gradient_op, loss, deployment_setting, strategy,
                    communication_DSL, None)

        # Init Superscaler_TF class
        sc.init(apply_gradient_op, loss, deployment_setting, strategy,
                communication_DSL, resource_pool)

        cache_dir = sc.get_cache_dir()
        # Check whether cache_dir is created
        if not os.path.exists(cache_dir):
            raise OSError
        # Check whether working_dir is sub_folder of cache_dir
        assert(os.path.samefile(
            cache_dir, os.path.dirname(sc.get_working_dir())))
        if not os.path.exists(sc.get_working_dir()):
            raise OSError

        for i in range(sc._graph_count):
            working_dir = sc.get_working_dir()
            tmp_rank_dir = os.path.join(working_dir, str(i))
            if not os.path.exists(tmp_rank_dir):
                raise OSError

            plan_path = os.path.join(tmp_rank_dir, 'plan.json')
            plan_ref = json.load(open(plan_path, 'r'))
            assert(plan_ref == sc._assigned_plan[i])

            model_desc_path = os.path.join(tmp_rank_dir, 'model_desc.json')
            model_desc_ref = json.load(open(model_desc_path, 'r'))
            assert(model_desc_ref == sc._graph_config)

            graph_path = os.path.join(tmp_rank_dir, 'graph.pbtxt')
            graph_ref = open(graph_path, 'r').read()
            assert(graph_ref == sc._partition_graphs[i])

    # TODO provide run support
    # sc.run()
