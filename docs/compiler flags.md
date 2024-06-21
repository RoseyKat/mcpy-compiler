# List of compiler flags
A list of possible compiler flags for each type of file.

To add compiler flags, add a flag to a file by making the first line a comment of the flag.

For example in a json file, have the first line be `//COMPILER_FLAG_HERE`.

# Universal
Universal compiler flags that work everywhere.

* `//PASS` - Doesn't compile the file.

# JSON
In brackets will disclose what type of json flags will work on.         
> `BP` meaning it will work on behavior pack json (items, entities, and blocks).          
> `GEN` meaning generic json, which is everything but `BP` usually

* `//BYTE` - Halt compilition as json and compile as byte file instead. (BP, GEN)