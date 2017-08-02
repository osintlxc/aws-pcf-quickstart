# pivotal-cloud-foundry-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
import os
import botocore
import botocore.exceptions

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['AWS_INTEGRATION_REGION']


def get_bucket_names(stack_name: str):
    parameter_store_keys = [
        "PcfOpsManagerS3Bucket",
        "PcfElasticRuntimeS3BuildpacksBucket",
        "PcfElasticRuntimeS3DropletsBucket",
        "PcfElasticRuntimeS3PackagesBucket",
        "PcfElasticRuntimeS3ResourcesBucket"
    ]

    ssm_client = boto3.client(
        service_name='ssm', region_name=aws_region, aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    parameter_names = ["{}.{}".format(stack_name, p) for p in parameter_store_keys]

    response = ssm_client.get_parameters(
        Names=parameter_names,
        WithDecryption=False
    )

    param_results = response.get("Parameters")

    buckets = [p.get('Value') for p in param_results]

    return buckets


def delete_bucket(bucket_name: str):
    s3_client = boto3.client(
        service_name='s3', region_name=aws_region, aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    try:
        contents = s3_client.list_objects_v2(Bucket=bucket_name).get('Contents')
        while contents is not None:
            delete_keys = [{'Key': o.get('Key')} for o in contents]
            s3_client.delete_objects(Bucket=bucket_name, Delete={
                'Objects': delete_keys
            })
            contents = s3_client.list_objects_v2(Bucket=bucket_name).get('Contents')
        s3_client.delete_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error = e.response.get('Error')
        if not error or error.get('Code') != 'NoSuchBucket':
            raise e


cf_client = boto3.client(
    service_name='cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

with open('../aws-pcf-concourse-state/stackid', 'r') as file:
    stackid = file.read().strip()
print("Deleting buckets for stack {}".format(stackid))

response = cf_client.describe_stacks(StackName=stackid)
stacks = response.get('Stacks')
stack_name = stacks[0].get('StackName')

buckets = get_bucket_names(stack_name)
print("Buckets {}".format(buckets))
for bucket in buckets:
    delete_bucket(bucket)

print("Deleting stack {}".format(stackid))
client.delete_stack(StackName=stackid)