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

import os
import sys
import time
import unittest

try:
    import pytest
except ImportError:
    class _MockMark:
        def __getattr__(self, name):
            return lambda func: func
    class _MockPytest:
        mark = _MockMark()
    pytest = _MockPytest()

from io import BytesIO as StringIO
import docker

from rocker.core import get_docker_client, docker_build
from rocker.os_detector import detect_os, _detect_os_cache


BENCHMARK_FAT_IMAGE = "rocker-benchmark-fat:latest"
BENCHMARK_STANDARD_IMAGE = "ubuntu:focal"

FAT_IMAGE_DOCKERFILE = """
FROM ubuntu:focal
RUN dd if=/dev/zero of=/large_file bs=1M count=500
"""


class RockerOSDetectorBenchmarkTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        client = get_docker_client()
        # Ensure standard image is available
        try:
            client.inspect_image(BENCHMARK_STANDARD_IMAGE)
        except docker.errors.APIError:
            print(f"Pulling {BENCHMARK_STANDARD_IMAGE} for benchmark...")
            client.pull(BENCHMARK_STANDARD_IMAGE)

        # Ensure fat image is available
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
            assert image_id, "Failed to build benchmark fat image"

    @pytest.mark.docker
    @pytest.mark.benchmark
    def test_benchmark_standard_image(self):
        """Benchmark OS detection on a standard-sized image across cold and warm runs."""
        # Run 1: Cold in-memory cache
        _detect_os_cache.clear()
        start = time.perf_counter()
        result1 = detect_os(BENCHMARK_STANDARD_IMAGE)
        duration1 = time.perf_counter() - start

        self.assertIsNotNone(result1)
        self.assertEqual(result1[0], "Ubuntu")
        self.assertEqual(result1[1], "20.04")

        # Run 2: Simulating subsequent CLI call (in-memory cache cleared)
        _detect_os_cache.clear()
        start = time.perf_counter()
        result2 = detect_os(BENCHMARK_STANDARD_IMAGE)
        duration2 = time.perf_counter() - start

        self.assertIsNotNone(result2)
        self.assertEqual(result2[0], "Ubuntu")

        print(f"\n[Benchmark] Standard image ({BENCHMARK_STANDARD_IMAGE}):")
        print(f"  Run 1 (cold cache):           {duration1:.3f}s")
        print(f"  Run 2 (simulated next CLI):   {duration2:.3f}s")

    @pytest.mark.docker
    @pytest.mark.benchmark
    def test_benchmark_fat_image(self):
        """Benchmark OS detection on a large (fat) image across cold and warm runs."""
        # Run 1: Cold in-memory cache
        _detect_os_cache.clear()
        start = time.perf_counter()
        result1 = detect_os(BENCHMARK_FAT_IMAGE)
        duration1 = time.perf_counter() - start

        self.assertIsNotNone(result1)
        self.assertEqual(result1[0], "Ubuntu")
        self.assertEqual(result1[1], "20.04")

        # Run 2: Simulating subsequent CLI call (in-memory cache cleared)
        _detect_os_cache.clear()
        start = time.perf_counter()
        result2 = detect_os(BENCHMARK_FAT_IMAGE)
        duration2 = time.perf_counter() - start

        self.assertIsNotNone(result2)
        self.assertEqual(result2[0], "Ubuntu")

        print(f"\n[Benchmark] Fat image ({BENCHMARK_FAT_IMAGE}):")
        print(f"  Run 1 (cold cache):           {duration1:.3f}s")
        print(f"  Run 2 (simulated next CLI):   {duration2:.3f}s")

    @pytest.mark.docker
    @pytest.mark.benchmark
    def test_benchmark_in_memory_cache(self):
        """Verify in-memory cache within same process returns instantaneously."""
        _detect_os_cache.clear()
        detect_os(BENCHMARK_STANDARD_IMAGE)

        start = time.perf_counter()
        cached_result = detect_os(BENCHMARK_STANDARD_IMAGE)
        cached_duration = time.perf_counter() - start

        self.assertIsNotNone(cached_result)
        self.assertLess(cached_duration, 0.05, "In-memory cache lookup took longer than 50ms")
        print(f"\n[Benchmark] In-memory cache hit duration: {cached_duration * 1000:.3f}ms")

    @pytest.mark.docker
    @pytest.mark.benchmark
    def test_benchmark_multiple_iterations(self):
        """Run multiple trials clearing cache each time to measure repeated CLI invocation latency."""
        iterations = 3
        times_standard = []
        times_fat = []

        for i in range(iterations):
            _detect_os_cache.clear()
            t0 = time.perf_counter()
            detect_os(BENCHMARK_STANDARD_IMAGE)
            times_standard.append(time.perf_counter() - t0)

            _detect_os_cache.clear()
            t0 = time.perf_counter()
            detect_os(BENCHMARK_FAT_IMAGE)
            times_fat.append(time.perf_counter() - t0)

        avg_standard = sum(times_standard) / len(times_standard)
        avg_fat = sum(times_fat) / len(times_fat)

        print(f"\n[Benchmark] Over {iterations} iterations (simulating cold CLI invocations):")
        print(f"  Standard image avg: {avg_standard:.3f}s (min={min(times_standard):.3f}s, max={max(times_standard):.3f}s)")
        print(f"  Fat image avg:      {avg_fat:.3f}s (min={min(times_fat):.3f}s, max={max(times_fat):.3f}s)")


if __name__ == "__main__":
    unittest.main()
