#!/usr/bin/env python3

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""Benchmark script comparing modern (--mount type=image) vs legacy OS detection."""

import argparse
from io import BytesIO as StringIO
import time
from unittest.mock import patch

import docker
from packaging.version import Version

from rocker.core import docker_build, get_docker_client
from rocker.os_detector import _detect_os_cache, detect_os, ensure_detector_image


BENCHMARK_FAT_IMAGE = "rocker-benchmark-fat:10G"
BENCHMARK_STANDARD_IMAGE = "ubuntu:focal"

FAT_IMAGE_DOCKERFILE = """
FROM ubuntu:focal
RUN dd if=/dev/zero of=/large_file bs=1M count=1000
"""


def setup_benchmark_images(client):
    try:
        client.inspect_image(BENCHMARK_STANDARD_IMAGE)
    except docker.errors.APIError:
        print(f"Pulling {BENCHMARK_STANDARD_IMAGE} for benchmark...")
        client.pull(BENCHMARK_STANDARD_IMAGE)

    try:
        client.inspect_image(BENCHMARK_FAT_IMAGE)
    except docker.errors.APIError:
        print(f"Building {BENCHMARK_FAT_IMAGE} for benchmark...")
        iof = StringIO(FAT_IMAGE_DOCKERFILE.strip().encode())
        image_id = docker_build(
            fileobj=iof,
            nocache=False,
            forcerm=True,
            tag=BENCHMARK_FAT_IMAGE
        )
        if not image_id:
            raise RuntimeError("Failed to build benchmark fat image")

    ensure_detector_image(client)


def benchmark_single_image(label, image_name):
    _detect_os_cache.clear()
    start = time.perf_counter()
    result_modern = detect_os(image_name)
    duration_modern = time.perf_counter() - start
    assert result_modern is not None and result_modern[:2] == ("Ubuntu", "20.04"), result_modern

    _detect_os_cache.clear()
    with patch('rocker.os_detector._get_docker_version', return_value=Version("27.5.1")):
        start = time.perf_counter()
        result_legacy = detect_os(image_name)
        duration_legacy = time.perf_counter() - start
    assert result_legacy is not None and result_legacy[:2] == ("Ubuntu", "20.04"), result_legacy

    diff = duration_legacy - duration_modern
    speedup = duration_legacy / duration_modern if duration_modern > 0 else float('inf')
    print(f"\n[Benchmark] {label} ({image_name}):")
    print(f"  Modern (--mount type=image):  {duration_modern:.3f}s")
    print(f"  Legacy (docker build+run+rm): {duration_legacy:.3f}s")
    print(f"  Differential:                 {diff:+.3f}s ({speedup:.2f}x faster)")


def benchmark_in_memory_cache():
    _detect_os_cache.clear()
    detect_os(BENCHMARK_STANDARD_IMAGE)

    start = time.perf_counter()
    cached_result = detect_os(BENCHMARK_STANDARD_IMAGE)
    cached_duration = time.perf_counter() - start
    assert cached_result is not None
    print(f"\n[Benchmark] In-memory cache hit duration: {cached_duration * 1000:.3f}ms")


def benchmark_multiple_iterations(iterations):
    times_standard_modern = []
    times_standard_legacy = []
    times_fat_modern = []
    times_fat_legacy = []

    for _ in range(iterations):
        _detect_os_cache.clear()
        t0 = time.perf_counter()
        detect_os(BENCHMARK_STANDARD_IMAGE)
        times_standard_modern.append(time.perf_counter() - t0)

        _detect_os_cache.clear()
        with patch('rocker.os_detector._get_docker_version', return_value=Version("27.5.1")):
            t0 = time.perf_counter()
            detect_os(BENCHMARK_STANDARD_IMAGE)
            times_standard_legacy.append(time.perf_counter() - t0)

        _detect_os_cache.clear()
        t0 = time.perf_counter()
        detect_os(BENCHMARK_FAT_IMAGE)
        times_fat_modern.append(time.perf_counter() - t0)

        _detect_os_cache.clear()
        with patch('rocker.os_detector._get_docker_version', return_value=Version("27.5.1")):
            t0 = time.perf_counter()
            detect_os(BENCHMARK_FAT_IMAGE)
            times_fat_legacy.append(time.perf_counter() - t0)

    avg_std_mod = sum(times_standard_modern) / len(times_standard_modern)
    avg_std_leg = sum(times_standard_legacy) / len(times_standard_legacy)
    avg_fat_mod = sum(times_fat_modern) / len(times_fat_modern)
    avg_fat_leg = sum(times_fat_legacy) / len(times_fat_legacy)

    std_diff = avg_std_leg - avg_std_mod
    std_speedup = avg_std_leg / avg_std_mod if avg_std_mod > 0 else float('inf')
    fat_diff = avg_fat_leg - avg_fat_mod
    fat_speedup = avg_fat_leg / avg_fat_mod if avg_fat_mod > 0 else float('inf')

    print(f"\n[Benchmark] Over {iterations} iterations (simulating cold CLI invocations):")
    print(f"  Standard image ({BENCHMARK_STANDARD_IMAGE}):")
    print(f"    Modern avg:       {avg_std_mod:.3f}s (min={min(times_standard_modern):.3f}s, max={max(times_standard_modern):.3f}s)")
    print(f"    Legacy avg:       {avg_std_leg:.3f}s (min={min(times_standard_legacy):.3f}s, max={max(times_standard_legacy):.3f}s)")
    print(f"    Differential:     {std_diff:+.3f}s ({std_speedup:.2f}x faster)")
    print(f"  Fat image ({BENCHMARK_FAT_IMAGE}):")
    print(f"    Modern avg:       {avg_fat_mod:.3f}s (min={min(times_fat_modern):.3f}s, max={max(times_fat_modern):.3f}s)")
    print(f"    Legacy avg:       {avg_fat_leg:.3f}s (min={min(times_fat_legacy):.3f}s, max={max(times_fat_legacy):.3f}s)")
    print(f"    Differential:     {fat_diff:+.3f}s ({fat_speedup:.2f}x faster)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-n", "--iterations", type=int, default=3,
        help="Number of iterations for multi-run average (default: 3)"
    )
    args = parser.parse_args()

    client = get_docker_client()
    setup_benchmark_images(client)

    benchmark_single_image("Standard image", BENCHMARK_STANDARD_IMAGE)
    benchmark_single_image("Fat image", BENCHMARK_FAT_IMAGE)
    benchmark_in_memory_cache()
    benchmark_multiple_iterations(args.iterations)


if __name__ == "__main__":
    main()
