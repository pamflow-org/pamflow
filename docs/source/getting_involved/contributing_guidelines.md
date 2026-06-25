# Contributing guidelines

We welcome all contributions that help improve the code, documentation, and overall functionality. Please follow these guidelines to ensure a smooth contribution process.

## Table of Contents
1. [Getting Started](#getting-started)
2. [How to Contribute](#how-to-contribute)
3. [Code Standards](#code-standards)
4. [Git Commit Names](#git-commit-names)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)
7. [Reporting Issues](#reporting-issues)

## Getting Started
1. Fork the repository and clone it locally:
  ```sh
  git clone <github link to the repo>
  cd pamflow
  ```
The [anonymized version of the repo](https://anonymous.4open.science/r/pamflow-DC88/) cannot be clonned and thus needs to be downloaded from the button on the upper right corner inside the link.
2. Create a new branch for your feature or bug fix:
   ```sh
   git checkout -b feature-branch
   ```
3. Install dependencies:
   ```sh
   pip install .
   ```

## How to Contribute
- **Bug Fixes:** If you find a bug, check if an issue already exists. If not, create a new issue and submit a fix.
- **Feature Requests:** Open an issue describing the feature before starting work.
- **Documentation:** Improvements to documentation are always welcome!

## Code Standards
- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python coding style.
- Use `ruff` for linting: [link](https://docs.kedro.org/en/stable/development/linting.html)
- Use type hints where possible:
  ```python
  def process_data(data: list) -> dict:
      # Processing logic
      return {}
  ```
- Follow `kedro` best practices:
  - Maintain a clear project structure using `kedro`'s default directory layout.
  - Use `kedro pipelines` to structure data workflows efficiently.
  - Leverage `kedro catalog` for data management and reproducibility.
  - Ensure modular, reusable, and well-documented nodes within pipelines.
  - Write tests for `kedro` nodes and pipelines to validate data processing logic.

## Git Commit Names
Use the following commit message conventions:
- **`BUILD`**: Indicates a change to the build system or external dependencies.
- **`DOC`**: Indicates a change to documentation.
- **`FEAT`**: Indicates a new feature being added to the code base.
- **`FIX`**: Indicates a bug fix.
- **`TEST`**: Indicates changes to the testing framework.

## Testing
- Ensure all changes include appropriate tests.
- Run tests using:
  ```sh
  pytest
  ```
- Add new test cases for any added functionality.

## Pull Request Process
1. Ensure your code follows the coding standards.
2. Run all tests before submitting.
3. Submit a pull request with a clear description of your changes.
4. Address any requested changes from reviewers.

## Reporting Issues
- When reporting an issue, provide clear reproduction steps and expected vs. actual behavior.
- Include relevant error messages, system details, and screenshots if applicable.
