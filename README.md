# mcpy-compiler
A niche little compiler made in python that will go through all your addon files and compile them to an output (such as com_mojang folder) and watch for any changes and compile them instantly!

# Features
* Automatic manifest generation. It will check what you have, such as scripts, and add it to the manifest automatically!

* Optimized outputs. Removes blank lines, and ignores comments in files. (excluding scripts)

* Pretty fast. I tested the compiler on a personal project that has about 2000~ files, and compiled them all in about 5 seconds!

# Getting started
Create a `config.json` file at the root directory of your project and set it up:    
<sub>Please note that the actual config cannot have comments, and the compiler will fail if you try run it with a commented config
```jsonc
{
    "output": "@com_mojang", // Where to compile output, use '@com_mojang' to go directly to com_mojang folder.
    "auto_manifest": true, // Whether to use the automatic manifest generation tool.
    "project_name": "test", // Project display name
    "project_description": "test", // Project description
    "target_version": "1.20.80", // Target minecraft version
    "script_entry": "scripts/Main.js", // If using scripts, where the entry point is
    "packs": [ // What packs you will be using `bp` and/or `rp`
        "bp",
        "rp"
    ],
    "show_compiled": false // Whether to display succesfully compiled files
}
```

Next run [compiler.py](https://github.com/RoseyKat/mcpy-compiler/blob/main/compiler.py) (or exe) at the root of your project. Which must have `BP` and/or `RP` folders. And you should now have a compiled project and you can actively modify your files and they will be compiled on save!

If you run into any problems please create a [github issue](https://github.com/RoseyKat/mcpy-compiler/issues/new)!

# Key notes
* This *might* work on mac and linux although I can't make any promises, as long as you have the `output` set to something else other than `@com_mojang`.
* Only png images will compile.
* Sometimes a file might compile twice in one go.
