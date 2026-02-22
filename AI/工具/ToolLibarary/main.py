import argparse
import importlib
import pkgutil
import sys


def discover_and_register_tools(subparsers: argparse._SubParsersAction) -> None:
    """
    Discover modules under the `tools` package and let each one register its
    own subcommand.

    Convention:
    - Preferred: module defines `register_subparser(subparsers)`
    - Fallback: module defines both `add_arguments(parser)` and `run(args)`
    """
    package_name = "tools"
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        return

    for module_info in pkgutil.iter_modules(package.__path__):
        module_name = module_info.name
        if module_name.startswith("_"):
            continue

        module = importlib.import_module(f"{package_name}.{module_name}")

        register = getattr(module, "register_subparser", None)
        if callable(register):
            register(subparsers)
            continue

        add_arguments = getattr(module, "add_arguments", None)
        run = getattr(module, "run", None)
        if callable(add_arguments) and callable(run):
            help_text = (getattr(module, "__doc__", "") or f"{module_name} tool").strip()
            short_help = help_text.splitlines()[0] if help_text else module_name
            parser = subparsers.add_parser(module_name, help=short_help, description=help_text or None)
            add_arguments(parser)
            parser.set_defaults(func=run)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="toolkit", description="Python CLI 工具集入口。")
    parser.add_argument("-v", "--version", action="version", version="0.1.0")
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    discover_and_register_tools(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if callable(func):
        result = func(args)
        return int(result) if isinstance(result, int) else 0
    # 未提供子命令时，默认打开主界面菜单
    try:
        # 优先尝试图形主界面
        from tools import gui_launcher
        return int(gui_launcher.run_gui_menu())
    except Exception:
        try:
            from tools import launcher
            return int(launcher.run_menu(None))
        except Exception:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())


