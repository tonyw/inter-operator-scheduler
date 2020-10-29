import json
import argparse
import numpy as np
import os
from ios.ir import Graph
from ios.visualizer import draw, draw_block
from ios.cost_model import IOSCostModel

argparser = argparse.ArgumentParser()
argparser.add_argument('--edir', type=str, required=True)
argparser.add_argument('--ename', type=str, required=True)
argparser.add_argument('--device', type=str, required=True)
argparser.add_argument('--graph', type=str, required=True)
argparser.add_argument('--bs', type=int, required=True)
argparser.add_argument('--warmup', type=int, required=False, default=2)
argparser.add_argument('--number', type=int, required=False, default=6)
argparser.add_argument('--repeat', type=int, required=False, default=6)

args = argparser.parse_args()
expr_dir = f'./outputs/{args.edir}/{args.ename}-{args.device}-g{args.graph}-bs{args.bs}-{args.warmup}-{args.number}-{args.repeat}'

#os.makedirs("./outputs", exist_ok=True)
#os.makedirs(f"./outputs/{args.ename}", exist_ok=True)
os.makedirs(expr_dir, exist_ok=True)


def main():
    logs = {}
    summary = []
    line = f'Argument: {args}'
    print(line)
    summary.append(line)

    with open(f'schedules/{args.graph}.json', 'r') as f:
        graph = Graph.from_config(json.load(f))

    cost_model = IOSCostModel()
    name = graph.name
    graph_latency = cost_model.get_graph_latency(graph, args.bs, warmup=args.warmup, number=args.number, repeat=args.repeat)
    block_latency = [np.mean(cost_model.get_block_latency(block, args.bs, args.warmup, args.number, args.repeat)) for block in graph.blocks]
    logs[name] = {}
    logs[name]['latency'] = graph_latency
    logs[name]['mean'] = float(np.mean(graph_latency))
    logs[name]['std'] = float(np.std(graph_latency))
    logs[name]['block_latency'] = block_latency
    line = f" {args.ename}: {np.mean(graph_latency):.4f}\n"
    print(line)
    summary.append(line)
    for bindex, block in enumerate(graph.blocks):
        block_dir = f'{expr_dir}/{name}_blocks'
        os.makedirs(block_dir, exist_ok=True)
        draw_block(block, f'{block_dir}/{bindex}.png', f'{name} block {bindex}, latency {block_latency[bindex]:.3f}')
    draw(graph, f"{expr_dir}/{name}.png", label=f'{name}, latency {float(np.mean(graph_latency)):.3f}')

    with open(f"{expr_dir}/{name}.json", "w") as f:
        json.dump(graph.export_config(), f, indent=2)
    with open(f'{expr_dir}/latency.json', 'w') as f:
        json.dump(logs, f, indent=2)
    with open(f'{expr_dir}/summary.txt', 'w') as f:
        f.write('\n'.join(summary))
    with open(f'{expr_dir}/arguments.txt', 'w') as f:
        json.dump(args.__dict__, f, indent=2)


main()

