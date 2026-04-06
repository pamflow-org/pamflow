# Installation instructions

To use **pamflow** you will need to:

```{contents}
   :depth: 1
   :local:
   :numbered:
```
If you are already familiar with Python, Git, and Conda you can skip the first two steps.

## 1. Install miniconda
To run **pamflow**, your computer needs Python and other required tools installed. We'll use Miniconda to install Python and related packages — it's a lightweight tool that keeps each project's environment separate and avoids conflicts.

Follow the official Miniconda installation guide for your operating system: [Installing Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install/overview).

## 2. Install Git

Git is a version control tool that lets you download and track project code. You will need it to clone the **pamflow** repository in the next step. Download and install Git for your operating system from the [official Git website](https://git-scm.com/downloads) — the default installation options work fine for most users.

## 3. Clone the repository

A repository is a storage space where a project's files and history are kept. To use **pamflow**, you need to download it through a process called *cloning*. 

Open a terminal on your computer:
- **Windows:** use the **Anaconda Prompt** (search for it in the Start menu after installing Miniconda — do not use the regular Command Prompt, as it won't have access to Conda commands)
- **macOS / Linux:** use the built-in **Terminal**

Then run:
```sh
git clone <github link to the repo>
cd pamflow
```

> **Note:** The [anonymized version of the repo](https://anonymous.4open.science/r/pamflow-DC88/) cannot be cloned directly. Instead, download it manually using the download button in the upper-right corner of that page, then unzip it and navigate into the folder using `cd pamflow`.

## 4. Install required packages

Now that Miniconda and the repository are ready, you can create a virtual environment and install the required packages. A virtual environment is like a private workspace where **pamflow** has its own copy of Python and its own tools, kept separate from other projects on your computer.

In the same terminal window (Anaconda Prompt on Windows), run:
```sh
conda create -n pamflow_env python=3.10.14
```

This may take a moment and will ask you to confirm by typing `Y`. This step is only required once.

Once the environment is created, activate it:
```sh
conda activate pamflow_env
```

> **Important:** Every time you want to use **pamflow**, you will need to activate this environment first.

Finally, install the required dependencies:
```sh
pip install .
```