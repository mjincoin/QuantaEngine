"""Command-line interface for QuantaEngine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import QuantaEngine
from .io import load_config, save_config
from .params import UniverseParams
from .visualize import save_diagnostics


def _cmd_init(args: argparse.Namespace) -> int:
    params = UniverseParams(name=args.name, seed=args.seed, grid_size=args.grid_size)
    save_config(params, args.out)
    print(f"Wrote configuration to {args.out}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    params = load_config(args.config)
    engine = QuantaEngine(params)
    result = engine.run(steps=args.steps, snapshot_every=args.snapshot_every)
    result.save(args.out)
    if args.plot:
        save_diagnostics(result, args.out)
    print(json.dumps(result.summary(), indent=2, sort_keys=True))
    print(f"Saved result to {Path(args.out).resolve()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quantaengine",
        description="Generate toy universes from tunable first-principles-inspired physics.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="write a starter YAML configuration")
    init.add_argument("--out", default="universe.yaml", help="output YAML path")
    init.add_argument("--name", default="demo-universe", help="universe name")
    init.add_argument("--seed", type=int, default=42, help="random seed")
    init.add_argument("--grid-size", type=int, default=128, help="lattice size per dimension")
    init.set_defaults(func=_cmd_init)

    run = sub.add_parser("run", help="run a universe simulation")
    run.add_argument("--config", required=True, help="YAML/JSON UniverseParams configuration")
    run.add_argument("--out", default="runs/demo", help="output directory")
    run.add_argument("--steps", type=int, default=128, help="number of integration steps")
    run.add_argument("--snapshot-every", type=int, default=16, help="snapshot interval")
    run.add_argument("--plot", action="store_true", help="save diagnostic PNG maps")
    run.set_defaults(func=_cmd_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
