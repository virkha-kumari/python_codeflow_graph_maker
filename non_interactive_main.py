import argparse
import os

from worker import dependency_store_maker, graph_maker


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a Python codebase and write a dependency report for one main file."
    )
    parser.add_argument("codebase_path", help="Root folder of the codebase to analyze")
    parser.add_argument("main_file", help="Entry-point .py file (absolute, or relative to codebase_path)")
    parser.add_argument("--exclude-dir", action="append", default=[],
                        help="Directory name to skip (repeatable). venv, .git, __pycache__ are always skipped.")
    parser.add_argument("--exclude-file", action="append", default=[],
                        help="File name to skip (repeatable)")
    args = parser.parse_args()

    codebase_root = os.path.abspath(args.codebase_path)
    main_file = args.main_file
    if not os.path.isabs(main_file):
        main_file = os.path.join(codebase_root, main_file)

    dependency_store, num_py_files = dependency_store_maker(
        folder_path=codebase_root,
        exclude_dirs=["venv", ".git", "__pycache__"] + args.exclude_dir,
        exclude_files=args.exclude_file,
    )

    main_file_rel = os.path.relpath(main_file, codebase_root).replace("\\", "/")
    print(f"Analyzed {num_py_files} Python files. Main file: {main_file_rel}")
    graph_maker(
        dependency_store=dependency_store,
        main_folder_path=codebase_root,
        main_file_path=main_file_rel,
    )


if __name__ == "__main__":
    main()
