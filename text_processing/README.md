## Basic Text Processing
This is a basic text processor that takes a data file of employee information and formats it. The employee data is also saved as a pickle file. The code for the project can be viewed [here](homework1_htk180000.py).

### How To Run
Use Python3 to run the homework1_htk180000.py file in the text_processing folder and provide a path to the data file. For example:

> python homework1_htk180000.py data/data.csv

The data file should contain entries where each line is 

> Last,First,Middle Initial,ID,Office phone

with the first line being the headers.

### Reflection
One of the strengths of Python for a text processing task like this is the built-in methods for strings such as title(), lower(), and upper() for easy edits to capitalization. Reading each entry of the data is also fairly simple with the way Python can iterate over all the lines of a file. On the other hand, using classes and objects is not as secure in Python as other langauges due to the lack of access modifiers, which could cause issues for larger projects.

While completing this assignment, I learned about saving objects as pickle files and using regular expressions in Python. Specifically, I found the fullmatch() useful for validating the format of strings. I also reviewed the use of sysargs and taking command line arguments as input for a Python program.