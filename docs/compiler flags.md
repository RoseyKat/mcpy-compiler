# List of compiler flags
A list of possible compiler flags for each type of file.

To add compiler flags, add a flag to a file by making the first line a comment of the flag.

For example in a json file, have the first line be `//COMPILER_FLAG_HERE`.

# Universal
Universal compiler flags that work everywhere.

* `//PASS` - Doesn't compile the file.
* `//BYTE` - Compile as bytes, lowest level of compiling.