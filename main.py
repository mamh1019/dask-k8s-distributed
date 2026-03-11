#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# main.py

"""
Dask-K8s 분산 처리 데모

Kubernetes 위에서 Dask 클러스터를 구성하고, 작업을 여러 Pod에 분산하여 병렬 처리하는 예제.
실제 프로덕션에서는 ROAS 예측, 코호트 분석 등 대용량 데이터 처리에 활용.
"""

import argparse
from dask_kubernetes.operator import KubeCluster
from dask.distributed import Client
import dask
import time


# -----------------------------------------------------------------------------
# 1. 클러스터 연결
# -----------------------------------------------------------------------------
cluster = KubeCluster.from_name(name="roas-cluster", namespace="dask-cluster")
client = Client(cluster)

print(f"Dashboard: {client.dashboard_link}")

cluster.scale(18)


# -----------------------------------------------------------------------------
# 2. 워커 태스크 정의
# -----------------------------------------------------------------------------
# Dask는 태스크를 직렬화하여 워커에 전달하므로,
# DB 커넥션, 직렬화 불가 객체는 인자로 넘기지 않음.


def worker_task(batch: list, task_id: int, options: dict) -> dict:
    """
    각 워커 Pod에서 실행되는 태스크.
    batch 단위로 데이터 집계 및 변환 수행.
    """
    try:
        import pandas as pd

        df = pd.DataFrame(batch)
        # 카테고리별 집계 (sum, mean, count)
        agg = (
            df.groupby("category", as_index=False)["value"]
            .agg(sum="sum", mean="mean", count="count")
            .to_dict(orient="records")
        )

        return {
            "task_id": task_id,
            "batch_size": len(batch),
            "total_sum": float(df["value"].sum()),
            "total_count": len(df),
            "aggregation": agg,
            "status": "success",
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "batch_size": len(batch),
            "status": "failed",
            "error": str(e),
        }


# -----------------------------------------------------------------------------
# 3. 분산 처리 실행
# -----------------------------------------------------------------------------
def run_distributed(tasks: list, batch_size: int) -> list:
    """태스크를 batch_size 단위로 나누어 워커에 분배 후 결과 수집."""
    if not tasks:
        return []

    batches = [tasks[i : i + batch_size] for i in range(0, len(tasks), batch_size)]

    lazy_results = [
        dask.delayed(worker_task)(batch, idx, {}) for idx, batch in enumerate(batches)
    ]

    try:
        results = dask.compute(*lazy_results)
        return list(results)
    except Exception as e:
        print(f"Cluster execution failed: {e}")
        raise


# -----------------------------------------------------------------------------
# 4. 메인 실행
# -----------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Dask-K8s distributed processing demo")
    parser.add_argument(
        "--tasks",
        type=int,
        default=100,
        help="Number of sample tasks to process (default: 100)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size per worker (default: 10)",
    )
    parser.add_argument(
        "--categories",
        type=int,
        default=5,
        help="Number of categories for grouping (default: 5)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 샘플 데이터: id, category, value
    sample_tasks = [
        {"id": i, "category": f"cat_{i % args.categories}", "value": i * 10}
        for i in range(args.tasks)
    ]

    print(f"Tasks: {len(sample_tasks)}, Batch size: {args.batch_size}")
    print("Distributed processing started...")

    start = time.time()
    results = run_distributed(sample_tasks, batch_size=args.batch_size)
    elapsed = time.time() - start

    # 결과 집계
    success = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]

    total_processed = sum(r.get("total_count", 0) for r in success)
    total_sum = sum(r.get("total_sum", 0) for r in success)
    throughput = total_processed / elapsed if elapsed > 0 else 0

    print(f"\n--- Summary ---")
    print(f"Batches: {len(results)} (success: {len(success)}, failed: {len(failed)})")
    print(f"Total processed: {total_processed} records")
    print(f"Total sum: {total_sum:,.0f}")
    print(f"Elapsed: {elapsed:.2f}s")
    print(f"Throughput: {throughput:.1f} records/sec")

    if failed:
        print(f"\nFailed batches: {[r['task_id'] for r in failed]}")

    print("\nSample result (first batch):")
    if success:
        r = success[0]
        agg_preview = str(r.get("aggregation", [])[:2])
        print(f"  task_id={r['task_id']}, total_sum={r['total_sum']}, agg={agg_preview}...")
