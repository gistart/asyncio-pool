# coding: utf8

import os
import sys
curr_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.split(curr_dir)[0])

import time
import argparse
import asyncio as aio
from asyncio_pool import AioPool, result_noraise


async def loadtest_spawn(tasks, pool_size, duration):
    futures = []
    async with AioPool(size=pool_size) as pool:
        for i in range(tasks):
            fut = await pool.spawn(aio.sleep(duration))
            futures.append(fut)

    return [result_noraise(f) for f in futures]


async def loadtest_spawn_n(tasks, pool_size, duration):
    futures = []
    async with AioPool(size=pool_size) as pool:
        for i in range(tasks):
            fut = await pool.spawn_n(aio.sleep(duration))
            futures.append(fut)

    return [result_noraise(f) for f in futures]


async def loadtest_map(tasks, pool_size, duration):
    async def wrk(i):
        await aio.sleep(duration)

    async with AioPool(size=pool_size) as pool:
        return await pool.map(wrk, range(tasks))


async def loadtest_itermap(tasks, pool_size, duration):
    async def wrk(i):
        await aio.sleep(duration)

    results = []
    async with AioPool(size=pool_size) as pool:
        async for res in pool.itermap(wrk, range(tasks)):
            results.append(res)

    return results


def print_stats(args, exec_time):
    ideal = args.task_duration * (args.tasks / args.pool_size)

    overhead = exec_time - ideal
    overhead_perc = ((exec_time / ideal) - 1) * 100

    per_task = overhead / args.tasks
    per_task_perc = (((args.task_duration + per_task) / args.task_duration) - 1) * 100

    print(f'{ideal:15.5f}s -- ideal result')
    print(f'{exec_time:15.5f}s -- were executing')
    print(f'{overhead:15.5f}s -- overhead total')
    print(f'{overhead_perc:15.5f}% -- overhead total percent')
    print(f'{per_task:15.5f}s -- overhead per task')
    print(f'{per_task_perc:15.5f}% -- overhead per task percent')


if __name__ == "__main__":
    methods = {
        'spawn': loadtest_spawn,
        'spawn_n': loadtest_spawn_n,
        'map': loadtest_map,
        'itermap': loadtest_itermap,
    }

    p = argparse.ArgumentParser()
    p.add_argument('method', choices=methods.keys())
    p.add_argument('--tasks', '-t', type=int, default=10**5)
    p.add_argument('--task-duration', '-d', type=float, default=0.2)
    p.add_argument('--pool-size', '-p', type=int, default=10**3)
    args = p.parse_args()

    print('>>> Running %d tasks in pool of size=%s, each task takes %.3f sec.' %
          (args.tasks, args.pool_size, args.task_duration))
    print('>>> This will run more than %.5f seconds' %
          (args.task_duration * (args.tasks / args.pool_size)))

    ts_start = time.perf_counter()
    m = methods.get(args.method)(args.tasks, args.pool_size, args.task_duration)
    aio.get_event_loop().run_until_complete(m)
    exec_time = time.perf_counter() - ts_start
    print_stats(args, exec_time)
