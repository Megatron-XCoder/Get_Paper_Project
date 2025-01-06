
# Get Papers List

This project fetches and filters PubMed papers based on author affiliations, allowing users to perform custom searches and save the results.

## Features
- Fetch PubMed papers based on a user-defined search query.
- Filter papers using specific criteria (e.g., author affiliations).
- Save filtered results to a specified file.
- Debug mode for additional insights during execution.


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/get-papers-list.git
   cd get-papers-list
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

---

## Usage

Run the script using Poetry:

### Basic Usage:
```bash
poetry run get-papers-list "<query>"
```

### Options:
- **`-d` / `--debug`**: Enable debug mode to view detailed logs.
- **`-f <filename>` / `--file <filename>`**: Specify the filename to save results.
- **`-h` / `--help`**: Show the help message and usage information.

### Examples:

1. **Basic Query**:
   ```bash
   poetry run get-papers-list "cancer research"
   ```

2. **With Debug Mode**:
   ```bash
   poetry run get-papers-list "machine learning" --debug
   ```

3. **Save Results to a File**:
   ```bash
   poetry run get-papers-list "genetics and human psychology" --file genetics.csv
   ```

4. **Show Help**:
    ```bash
   poetry run get-papers-list -h
   ```

---

## Dependencies

This project uses the following Python package:
- [requests](https://pypi.org/project/requests/): For making HTTP requests.

Dependencies are managed with Poetry. All required packages are listed in the `pyproject.toml` file.

---

## Debugging
Enable debug mode using the `-d` or `--debug` flag to display detailed logs about the script's execution, including fetched and filtered data.

---
