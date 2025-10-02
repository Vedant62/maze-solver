import argparse
import csv
from collections import defaultdict

def load_rows(csv_path):
    rows = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

def to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def to_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def aggregate(rows):
    by_method = defaultdict(list)
    for r in rows:
        by_method[r.get('method','unknown')].append(r)
    agg = {}
    for m, rs in by_method.items():
        n = len(rs)
        nodes_explored = sum(to_int(r.get('nodes_explored', 0)) for r in rs)
        path_len = sum(to_int(r.get('path_len', 0)) for r in rs)
        completed = sum(to_int(r.get('completed', 0)) for r in rs)
        solve_seconds = sum(to_float(r.get('solve_seconds', 0.0)) for r in rs)
        agg[m] = {
            'runs': n,
            'avg_nodes_explored': nodes_explored / n if n else 0,
            'avg_path_len': path_len / n if n else 0,
            'success_rate': completed / n if n else 0,
            'avg_solve_seconds': solve_seconds / n if n else 0,
        }
    return agg

def plot_aggregates(agg, save_path=None, show=True):
    import matplotlib.pyplot as plt
    methods = sorted(agg.keys())
    avg_nodes = [agg[m]['avg_nodes_explored'] for m in methods]
    avg_time = [agg[m]['avg_solve_seconds'] for m in methods]
    success = [agg[m]['success_rate'] for m in methods]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    axes[0].bar(methods, avg_nodes, color='#4C78A8')
    axes[0].set_title('Avg Nodes Explored')
    axes[0].set_ylabel('nodes')
    axes[0].set_xticklabels(methods, rotation=20, ha='right')

    axes[1].bar(methods, avg_time, color='#F58518')
    axes[1].set_title('Avg Solve Time (s)')
    axes[1].set_ylabel('seconds')
    axes[1].set_xticklabels(methods, rotation=20, ha='right')

    axes[2].bar(methods, success, color='#54A24B')
    axes[2].set_title('Success Rate')
    axes[2].set_ylabel('ratio')
    axes[2].set_ylim(0, 1)
    axes[2].set_xticklabels(methods, rotation=20, ha='right')

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print('Saved plot to', save_path)
    if show:
        plt.show()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('csv_path', help='Path to results CSV')
    p.add_argument('--save', help='Path to save PNG of plots (optional)', default=None)
    p.add_argument('--no-show', action='store_true', help='Do not open an interactive window')
    args = p.parse_args()

    rows = load_rows(args.csv_path)
    if not rows:
        print('No rows found in', args.csv_path)
        return
    agg = aggregate(rows)
    plot_aggregates(agg, save_path=args.save, show=not args.no_show)

if __name__ == '__main__':
    main()


