from datetime import datetime

import pytz

from kfp import dsl
from kfp import gcp


def mlp_task_op(
    image_tag: str,
    task: str,
    project: str,
    batch_size: int,
    epochs: int,
    chunk_size: int,
    cycle_length: int,
    job_bucket: str,
    job_output_path_prefix: str,
    job_output_path_suffix: str,
    table_id: str,
) -> dsl.ContainerOp:

    return dsl.ContainerOp(
        name='Train model',
        image="gcr.io/{}/gcp-demo1:{}".format(project, image_tag),
        arguments=[
            task, 
            '--table-id', table_id,
            "--batch-size", batch_size,
            '--job-dir', "gs://{}/{}/{}".format(
                job_bucket,
                job_output_path_prefix,
                job_output_path_suffix
            ),
            '--epochs', epochs,
            '--chunk-size', chunk_size
        ]
    )

@dsl.pipeline(
name='GCP Demo 1 MLP Trainer',
description='A trainer that does end-to-end distributed training for a multi-layer perceptron model.'
)
def mlp_train_pipeline(
    project: str,
    job_output_path_suffix: str,
    image_tag = 'training',
    batch_size: int = 64,
    epochs: int = 1,
    chunk_size: int = 5000000,
    cycle_length: int = 8,
    task: str = 'train',
    job_bucket: str = 'gcp-cert-demo-1',
    job_output_path_prefix: str = 'model/output',
    table_id: str = 'finaltaxi_encoded',
    gpu_count: int = 0,
    gpu_type: str = 'nvidia-tesla-k80',
    cpu_request: str = '6000m',
    cpu_limit: str = '6000m',
    mem_request: str = '40G',
    mem_limit: str = '40G'
):
    _train_op = mlp_task_op(
        image_tag=image_tag,
        task=task,
        project=project,
        batch_size=batch_size,
        chunk_size=chunk_size,
        job_bucket=job_bucket,
        job_output_path_prefix=job_output_path_prefix,
        job_output_path_suffix=job_output_path_suffix,
        table_id=table_id,
        epochs=epochs,
        cycle_length=cycle_length,
    ).set_display_name(
        'Train'
    ).set_image_pull_policy(
        'Always'
    ).set_cpu_request(
        cpu_request
    ).set_cpu_limit(
        cpu_limit
    ).set_memory_request(
        mem_request
    ).set_memory_limit(
        mem_limit
    )
    # .set_gpu_limit(1).add_node_selector_constraint(
    #         'cloud.google.com/gke-accelerator', 'nvidia-tesla-k80'
    # )

    dsl.get_pipeline_conf().add_op_transformer(
        gcp.use_gcp_secret()
    )