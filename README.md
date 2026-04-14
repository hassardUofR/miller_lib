# miller_lib
Python library package for integrated photonic design in the Ben Miller lab

Installation and use:
    GDSFactory caused some issues with the IPython version used by Spyder (my usual Python compiler). This is not the only way to run GDSFactory, but it is the simplest way to make sure it doesn't interfere with any other software or package versions on a computer.
 - Download GitHub to the computer and clone this GitHub repository to a folder OR
   Download the code from GitHub to a local folder.
 - Open the command prompt (I used Anaconda) and move to the folder where the code was saved 
   "cd path_to_folder_where_the_GitHub_package_was_downloaded"
 - Install UV (a Python package manager) if it is not installed: "pip install uv"
 - Run "uv pip install gdsfactory numpy scipy matplotlib". This will install these python packages into  a virtual Python environment that can be used to run files with this package.
 - To run a file using this environment, copy the file to the folder where the GitHub package was placed and then run "uv run filename.py".

 - After the first installation, files can be run with the "cd path_to_folder" and "uv run filename.py" steps.

    When writing a Python file, place the file in the folder where the miller_lib folder was downloaded, and include the line "import miller_lib as ml", whereupon the functions can be called with a line such as "ml.function_name(args,**kwargs)".


Package philosophy:
    The purpose of this package is to build a PIC design library of functions and classes that can be used to build PIC biosensors for the Miller lab at the University of Rochester. The package is loosely based on the OptoDesigner library from Michael Bryan, but is written in GDSFactory for Python. Additionally, the approach is more modular: building the blocks we can use to easily, quickly, and intuitively build and modify PIC designs.

    GDSFactory is built around the Component class, a building block that can hold geometries or other Components that can be exported into a GDS file. Most of the functions in this library return a Component and can be combined together into a single PIC Component.
    Example Python files are included in the test_files subfolder, but must be copied into the higher-level folder where the miller_lib code was downloaded to access the local package. See especially the "1x4PIC_test.py" file for an example of combining multiple Components to create a PIC, and "test_package.py" for a simple script to verify that the package is working.