# **pamflow** minimal setup

Before getting started with your tasks on the Guaviare Project, you need to install the dependencies required by **pamflow**:

* Miniconda
* Required packages 

In this section we provide useful resources for installation in any operative system. If you are already familiar with Python and Conda you can skip this step and [create your environment and install dependencies using PIP.](../contributing_guidelines.md#getting-started)



***Table of Contents***: 
1. [Install Miniconda](#install-miniconda)
2. [Clone repository](#clone-repository)
2. [Install required packages](#install-requiered-packages)

### Install Miniconda
Python is a programming language upon which **pamflow** is programmed. For your computer to undestand the commands inside **pamflow**'s code, Python should be installed. Instead of installing it directly we use Miniconda.Miniconda is a lightweight tool that lets you install Python and keep each project’s tools separate, so they don’t interfere with each other. For installing it, follow the tutorial that best suits you and your opperative system:

| Operative System | Language | Video                                                                         |
|------------------|----------|-------------------------------------------------------------------------------|
| Windows          | English  | [Link to the video (Up to 2:30)](https://www.youtube.com/watch?v=EBbcsjBSEi8) |
| Windows          | Spanish  | [Link to the video (Up to 1:35)](https://www.youtube.com/watch?v=n8HkaPEeJFs) |
| macOS            | English  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |
| macOS            | Spanish  | [Link to the video (Up to 1:30)](https://www.youtube.com/watch?v=WdXdl0C0jfE) |

### Clone repository

A repository is a storage space where a project’s files and history are kept, so you can organize your work, track changes, and share it with others. The code for **pamflow** is stored in a repository, so for using it you need to download it through a process called *cloning the repository*. For doing so open any terminal on you computer and run 
```sh
git clone https://github.com/pamflow/pamflow
cd pamflow
```

### Install required packages
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
   pip install -r requirements-win.txt
   ```
if in a Windows or  
 ```sh
   pip install -r requirements-mac.txt
   ```
if in a mac. This might also take a while but fortunatelly it has to be done only once. The only step you need to repeat every time you want to use your environment is activating your environment




**pamflow** is menat to be used exclusively through a terminal in any operative system, but, optionally, you might find more friendly and confortable to interact with it through a code editor such as VS Code, PyCharm, Spider, Atom or any other of your preference. But again, this is completely optional.


