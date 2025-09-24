# Installation instructions

To use **pamflow** you will need to:
1. [Install Miniconda](#1-install-miniconda)
2. [Clone repository](#2-clone-repository)
2. [Install required packages](#3-install-required-packages)

If you are already familiar with Python and Conda you can skip the first step and [create your environment and install dependencies using PIP.](../contributing_guidelines.md#getting-started)

## 1. Install miniconda
Python is the programming language upon which **pamflow** is programmed. For your computer to undestand the commands inside **pamflow**'s code, Python should be installed. Instead of installing it directly we use Miniconda, a lightweight tool that lets you install Python and keep each project’s tools separate, so they don’t interfere with each other. For installing it, follow the tutorial that best suits you and your opperative system:

| Operative System | Language | Video                                                                         |
|------------------|----------|-------------------------------------------------------------------------------|
| Windows          | English  | [Link to the video (Up to 2:30)](https://www.youtube.com/watch?v=EBbcsjBSEi8) |
| Windows          | Spanish  | [Link to the video (Up to 1:35)](https://www.youtube.com/watch?v=n8HkaPEeJFs) |
| macOS            | English  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |
| macOS            | Spanish  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |

## 2. Clone repository

A repository is a storage space where a project’s files and history are kept, so you can organize your work, track changes, and share it with others. The code for **pamflow** is stored in a repository. For using it you need to download it through a process called *cloning the repository*. Open any terminal on you computer and run 
```sh
git clone https://github.com/pamflow-org/pamflow.git
cd pamflow
```

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
From now on every time you want to use **pamflow** you will have to activate your environment. Finally, install all the required dependencies by r unning 
   
```sh
pip install .
```
