# Installation instructions

To use **pamflow** you will need to:

```{contents}
   :depth: 1
   :local:
   :numbered:
```
If you are already familiar with Python and Conda you can skip the first step.

## 1. Install miniconda
To run **pamflow**, your computer needs Python and other required tools installed. We’ll use Miniconda to install Python and related packages— it’s a lightweight tool that keeps each project’s environment separate and avoids conflicts. Follow the installation guide for your operating system:

| Operative System | Language | Video                                                                         |
|------------------|----------|-------------------------------------------------------------------------------|
| Windows          | English  | [Link to the video (Up to 2:30)](https://www.youtube.com/watch?v=EBbcsjBSEi8) |
| Windows          | Spanish  | [Link to the video (Up to 1:35)](https://www.youtube.com/watch?v=n8HkaPEeJFs) |
| macOS            | English  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |
| macOS            | Spanish  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |

## 2. Clone repository

A repository is a storage space where a project’s files and history are kept, so you can organize your work, track changes, and share it with others. The code for **pamflow** is stored in a repository. For using it you need to download it through a process called *cloning the repository*. Open any terminal on you computer and run 
```sh
git clone <github link to the repo>
cd pamflow
```
The [anonymized version of the repo](https://anonymous.4open.science/r/pamflow-DC88/) cannot be clonned and thus needs to be downloaded from the button on the upper right corner inside the link.
## 3. Install required packages
Now that Miniconda is installed, you can create a virtual environment and install the required packages for the download repository. A virtual environment is like a private workspace on your computer where a project can have its own copy of Python and its own tools. Virtual environments are important because they keep each project’s tools and settings separate, so you can work on different projects without them breaking or interfering with each other.

After running the command for cloning the repository, run 

```sh
conda create -n pamflow_env python=3.10.14
```
It might take a while and might require you to confirm you want to create the new environment by typing "Y" (yes). But don't worry, this step is only required once. When the environment is created it still needs to be activated. You can do so by running 

```sh
conda activate pamflow_env
```
From now on every time you want to use **pamflow** you will have to activate your environment. 
   
Finally, install the required dependencies 

```bash
pip install .
```
