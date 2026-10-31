# 🔄 Python Code Flow Graph Maker

A Python code analysis and visualization tool that generates dependency graphs for Python codebases. It parses every file with Python's `ast` module, maps import relationships between your own modules, the standard library and third-party libraries, detects I/O operations (with line numbers) from a built-in database of 122 patterns, and draws a color-coded dependency graph that starts from the entry file you choose.

## 🎯 Features

- **Static code analysis** with AST parsing. No code is executed.
- **Dependency tracking** between custom modules, standard-library modules and external libraries.
- **I/O operation detection**: 122 patterns across about 40 libraries and standard-library modules, each hit recorded with its line number.
- **Function/class usage tracking**: calls and attribute accesses are mapped back to their source module through the alias table (`import pandas as pd` → `pd.read_csv` is recorded as `pandas.read_csv`).
- **Dependency graph** of the chosen main file, followed recursively through local modules, with color-coded nodes, edge labels and a legend.
- **Web GUI** (Streamlit) with a step-by-step workflow, plus a **command-line interface** that takes arguments.
- **Exports**: JSON analysis results, a detailed text report for the main file, and a 300 DPI PNG of the graph (GUI).
- **Codebase statistics**: totals plus top-5 lists of the largest files, most-imported modules and I/O-heavy files.
- **Configurable exclusions** for directories and files, and an editable list of "pre-built" libraries.
- **Error handling**: syntax errors, encoding errors and unreadable files are reported per file and skipped, so one bad file doesn't stop the analysis.

## 🏗️ Architecture & Algorithms

### Core analysis: two-pass AST parsing

1. **First pass: import analysis** (top-level statements of each file)
   - Direct imports: `import module`
   - Aliased imports: `import module as alias`
   - From imports: `from module import item`
   - Relative imports: `from . import item`
   - Star imports: `from module import *`
   - Future imports: `from __future__ import feature`
   - Builds the alias map used for usage tracking.

2. **Second pass: function and I/O analysis** (the whole tree via `ast.walk`)
   - Finds function calls and attribute accesses.
   - Maps each call to its source module using the alias map.
   - Matches calls against the I/O pattern database (plus special cases such as `open()`, `Path(...).open()` and `DataLoader(...)`).
   - Records each I/O operation with its line number.

### Dependency graph generation: recursive resolution

```text
Algorithm: RecursiveDependencyGraph
Input:  main_file, dependency_store, prebuilt_libs
Output: directed graph G

1. Initialize empty directed graph G
2. Add main_file as the root node (yellow, square)
3. For each import in the current file:
   a. Try to map the module to a local file (root-level, then relative to the importing file)
   b. If found (custom module):
        add a red node and recurse into that file's imports
   c. Else if it is a stdlib module or listed in prebuilt_libs.txt:
        add a green node
   d. Else:
        add a purple node (unresolved)
4. Add an edge from each dependent to its dependency
5. Track visited nodes so circular imports do not loop forever
6. Shell layout with the main file at the center
```

### I/O operation detection

The pattern database in `analyzer.py` (`_is_io_operation`) contains **122 patterns**:

#### Basic file operations
- `open()`, `gzip.open`, `bz2.open`, `lzma.open`, `io.open`, `io.StringIO`, `io.BytesIO`, `io.TextIOWrapper`

#### Data science and ML
- **Pandas**: `read_csv`, `read_json`, `read_excel`, `read_parquet`, `read_feather`, `read_hdf`, `read_sql`, `read_html`, `read_xml`, and the matching `to_*` writers
- **NumPy**: `load`, `save`, `loadtxt`, `savetxt`, `fromfile`, `tofile`, `genfromtxt`
- **PyTorch**: `load`, `save`, `load_state_dict`, `save_state_dict`, `DataLoader`
- **Scikit-learn / joblib**: `load_svmlight_file`, `joblib.load`, `joblib.dump`

#### Serialization and configuration
- **JSON**: `load`, `dump`, `loads`, `dumps`
- **Pickle**: `load`, `dump`, `loads`, `dumps`
- **CSV**: `reader`, `writer`, `DictReader`, `DictWriter`
- **YAML**: `safe_load`, `dump`, `safe_dump`
- **TOML**: `load`, `dump`, `loads`, `dumps`
- **ConfigParser**: `read`, `write`

#### Database and network
- **SQLite**: `sqlite3.connect`
- **SQLAlchemy**: `create_engine`
- **Requests**: `get`, `post`, `put`, `delete`
- **urllib**: `urllib.request.urlopen`, `urllib.request.urlretrieve`

#### File system and archives
- **Pathlib**: `Path.open`, `read_text`, `write_text`, `read_bytes`, `write_bytes`, `mkdir`, `rmdir`, `unlink`, `touch`
- **Shutil**: `copy`, `copy2`, `copyfile`, `copytree`, `move`, `rmtree`
- **Zipfile**: `ZipFile`, `PyZipFile`, `open`
- **Tarfile**: `open`, `TarFile`
- **Rarfile**: `RarFile`, `RarFile.extract`

#### Specialized libraries
- **Images**: `PIL.Image.open`, `PIL.Image.save`, `cv2.imread`, `cv2.imwrite`
- **Audio**: `librosa.load`, `librosa.output.write_wav`
- **HDF5**: `h5py.File`, `h5py.Group.create_dataset`, `h5py.Dataset.read`
- **Excel**: `openpyxl.load_workbook`, `openpyxl.Workbook.save`
- **XML**: `xml.etree.ElementTree.parse` / `write`, `lxml.etree.parse` / `write`
- **PDF**: `PyPDF2.PdfReader`, `PyPDF2.PdfWriter.write`

#### Cloud storage
- **AWS**: `boto3.client`
- **Google Cloud**: `google.cloud.storage.Client`
- **Azure**: `azure.storage.blob.BlobServiceClient`

#### Visualization and web
- **Matplotlib**: `pyplot.savefig`, `pyplot.imsave`
- **Plotly**: `io.write_html`, `io.write_image`
- **Seaborn**: `savefig`
- **Altair**: `save`, `renderer.save`
- **Streamlit**: `file_uploader`, `download_button`

## 🛠️ Technical Implementation

### Key components

| File | Role |
|---|---|
| `analyzer.py` | AST parsing and analysis engine: imports, function usage, I/O detection |
| `dependency_store.py` | Stores per-file results, computes summary statistics and analytics, saves/loads JSON |
| `worker.py` | Walks the codebase, prints the report, builds and draws the main-file dependency graph |
| `gui.py` | Streamlit web interface with step-by-step workflow |
| `non_interactive_main.py` | Command-line entry point |
| `prebuilt_libs.txt` | Library names treated as "pre-built" (green nodes). Edit to taste. |

### Data structure

```python
DependencyStore = {
    "files": {file_path: {
        "imports": [module_names],
        "io_count": int,
        "function_usage": {module: [functions]}
    }},
    "modules": {module_name: [dependent_files]},
    "io_operations": {file_path: [operations_with_line_numbers]},
    "function_usage": {file_path: {module: [functions]}},
    "file_info": {file_path: {
        "path": str,
        "size": int,
        "lines": int,
        "empty": bool
    }},
    "summary": {
        "total_files": int,
        "total_imports": int,
        "total_io_operations": int,
        "total_lines": int,
        "empty_files": int
    }
}
```

### Analytics methods

- `get_summary()`: overall statistics for the codebase
- `get_files_with_io()`: files containing I/O operations
- `get_largest_files(limit)`: largest files by line count
- `get_most_imported_modules(limit)`: most frequently imported modules
- `get_files_by_io_count(limit)`: files with the most I/O operations
- `get_file_io_operations(file_path)`: I/O operations of one file
- `get_file_info(file_path)`: file metadata and statistics
- `get_module_dependents(module)`: files that import a module

### Visualization

- **Node types**:
  - 🟡 Yellow square: main entry file
  - 🔴 Red circle: custom/local module
  - 🟢 Green circle: standard-library module or a library listed in `prebuilt_libs.txt`
  - 🟣 Purple circle: unresolved module (not local, not stdlib, not in `prebuilt_libs.txt`)
- **Layout**: shell layout with the main file at the center
- **Edge labels**: `dependent --> dependency` (names shortened to 4 characters)
- **Legend** explaining colors and edge labels
- **Export**: 300 DPI PNG from the GUI

## 📋 Requirements

- Python 3.10+ (uses `sys.stdlib_module_names`)
- `streamlit`, `networkx`, `matplotlib`, `numpy` (see `requirements.txt`)

## 🚀 Installation & Usage

```bash
git clone https://github.com/virkha-kumari/python_codeflow_graph_maker.git
cd python_codeflow_graph_maker
pip install -r requirements.txt
```

Run everything from the repository folder, because `prebuilt_libs.txt` and `output_files/` are resolved relative to the working directory.

### Web UI (Streamlit)

```bash
streamlit run gui.py
```

A step-by-step flow: pick a folder (type the path, or use the tkinter folder picker on a desktop session), choose the main file, set exclusions, run the analysis, view the graph and statistics, then export the JSON, the text report and the 300 DPI PNG.

### Command line

```bash
python non_interactive_main.py path/to/codebase path/to/codebase/main.py --exclude-dir tests --exclude-dir docs
```

Prints the per-file analysis, summary statistics, graph nodes and edges, and writes the JSON and text report to `output_files/`. It does not save the graph image (use the GUI for the PNG).

| Argument | Meaning |
|---|---|
| `codebase_path` | Root folder of the codebase to analyze |
| `main_file` | Entry-point `.py` file (absolute, or relative to `codebase_path`) |
| `--exclude-dir NAME` | Directory name to skip (repeatable). `venv`, `.git`, `__pycache__` are always skipped. |
| `--exclude-file NAME` | File name to skip (repeatable) |

Example on this repo itself:

```bash
python non_interactive_main.py . gui.py
```

## 📊 Output Formats

### JSON analysis results
The full `DependencyStore` structure above, saved as `output_files/dependencies_<folder>.json`.

### Detailed text report
Saved as `output_files/detailed_deps_<folder>.txt`:
- Dependency relationships of the main file, with module types
- I/O operations of the main file, with line numbers
- Analysis summary (files, imports, I/O operations, lines, empty files)

### Console report
- Per-file imports, I/O operations with line numbers, and function usage by module
- Analysis summary and top-5 lists for the largest files, most-imported modules and I/O-heavy files

### Visual graph
- Color-coded dependency graph with legend and edge labels
- 300 DPI PNG export (GUI)

## 📁 Demo output

The two files committed in `output_files/` are **demo output results**, produced by running the tool on this repo itself (main file `gui.py`). They are kept so you can see what to expect before running anything:

- `output_files/dependencies_python_codeflow_graphmaker.json`: the JSON dump of the analysis
- `output_files/detailed_deps_python_codeflow_graphmaker.txt`: the text report

The absolute paths inside them (`D:\Projects\python_codeflow_graphmaker\...`) are from the author's machine and are left as they are on purpose. Your own run will show your own paths. New output written to `output_files/` is gitignored, so your results are not committed by accident.

## ⚠️ Assumptions & Limitations

### Assumptions
1. Run from the repository folder (for `prebuilt_libs.txt` and `output_files/`).
2. Only `.py` and `.pyw` files are analyzed.
3. Module-to-file resolution relies on file and folder names.
4. Source files are syntactically valid Python. Files that aren't are reported and skipped.
5. Source files are UTF-8. Files that aren't are reported and skipped.

### Limitations
1. The graph covers the dependencies of **one main file**, not the whole codebase at once.
2. Dynamic imports (`importlib.import_module`, `__import__`) and imports built from strings are not detected.
3. Imports inside functions, classes or `if`/`try` blocks are not recorded (only top-level imports are).
4. Static analysis only. Runtime behavior is not observed.
5. Dependencies of external packages are not followed.
6. The graph is a static matplotlib figure. Large graphs get crowded.
7. Behavior on very large codebases (1000+ files) is untested.
8. No automated test suite yet. It has been run on small projects, including itself.

### Known issues
- Relative imports with complex parent-directory structures may resolve incorrectly.
- Module aliasing in complex scenarios.
- Some edge cases in star-import analysis.
- Limited support for namespace packages.

## 🔧 Customization

### Adding new I/O patterns
Add entries to the `io_patterns` set in `_is_io_operation()` in `analyzer.py`:

```python
io_patterns = {
    # Add your custom patterns here
    "your_library.read_data",
    "your_library.save_data",
    # ... existing patterns
}
```

### Pre-built libraries
Add library names to `prebuilt_libs.txt`, one per line, to have them drawn as green nodes.

### Node colors
Colors are set in `graph_maker()` in `worker.py` (`yellow`, `red`, `green`, `purple`) and can be changed there.

## 🧑‍💻 Concepts / Libraries Used

- **Python `ast` module**: static code analysis
- **NetworkX**: graph construction and layout
- **Matplotlib**: graph rendering and PNG export
- **Streamlit**: web interface

## Licence

None yet. Add one before reusing the code.

---

**Made with ❤️ for the Python community. If something doesn't work, please open an issue!**
