#!/usr/bin/env python3

# coding=utf-8
# Copyright 2020 The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# this script dumps information about the environment

import os
import sys

import transformers


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

print("Python version:", sys.version)
print("transformers version:", transformers.__version__)

try:
    import torch

    print("Torch version:", torch.__version__)
    print("Cuda available:", torch.cuda.is_available())
    print("Cuda version:", torch.version.cuda if torch.cuda.is_available() else None)
    print("CuDNN version:", torch.backends.cudnn.version() if torch.cuda.is_available() else None)
    print("Number of GPUs available:", torch.cuda.device_count() if torch.cuda.is_available() else 0)
    print("NCCL version:", torch.cuda.nccl.version() if torch.cuda.is_available() else None)
except ImportError:
    print("Torch version:", None)

try:
    import deepspeed

    print("DeepSpeed version:", deepspeed.__version__)
except ImportError:
    print("DeepSpeed version:", None)

try:
    import tensorflow as tf

    print("TensorFlow version:", tf.__version__)
    print("TF GPUs available:", bool(tf.config.list_physical_devices("GPU")))
    print("Number of TF GPUs available:", len(tf.config.list_physical_devices("GPU")) if bool(tf.config.list_physical_devices("GPU")) else 0)
except ImportError:
    print("TensorFlow version:", None)
