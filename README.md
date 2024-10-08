# mcpy-compiler
A niche little compiler made in python that will go through all your addon files and compile them to an output (such as com_mojang folder) and watch for any changes to compile them instantly!

# Features
* Automatic manifest generation. It will check what you have, such as scripts, and add it to the manifest automatically!

* Optimized outputs. Removes blank lines, and ignores comments in files. (excluding scripts)

* Pretty fast. I tested the compiler on a personal project that has about 2000~ varying files, and compiled them all in about 3 seconds!

* Convert jpeg and webp to png. The compiler will automatically convert jpeg and webp images to png!

* Automatic texture defining. The compiler can go through all your textures and place them in `item_texture.json` automatically with no need to do it manually. (the texture definition will be the filename, works also for blocks, and texture list)

* Build projects into addons easily! Can compile all your files and then neatly place them into an mcaddon file!

* Search & Replace words/characters. Use `searcher.json` and insert a keyword to find in each file and replace.

# Getting started
Create a `config.json` file at the root directory of your project and set it up:    
You can use this [example config](https://github.com/RoseyKat/mcpy-compiler/blob/main/example_config.json)      
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
    "show_compiled": false, // Whether to display succesfully compiled files
    "compile_confusing_files": false // Whether to compile unknown or confusing files, if true, the compiler will compile them as a bytes file.
    "auto_texture_defining": true, // Whether to use the auto texture defining feature.
    "auto_textures_do": [ // Which textures to define if `auto_texture_defining` is `true`
        "items",
        "blocks",
        "list"
    ],
    "show_dates": true, // Whether to show the date and time when a file compiles (`show_compiled` must be true)
    "use_searcher": true // Whether to compile with the searcher.json keys.
}
```

Next create a python script at the root directory of your project, and imort `mcpy_compiler`, you may tinker with it, but if you want to just get to it call `mcpy_compiler.run()` and it will do everything you need it to do!

```py
from mcpy_compiler import mcpy_compiler
mcpy_compiler.run()
```

To build a project:
```py
from mcpy_compiler import mcpy_compiler
mcpy_compiler.build(True, True)
```

If you run into any problems please create a [github issue](https://github.com/RoseyKat/mcpy-compiler/issues/new)!

# Key notes
* This *might* work on mac and linux although I can't make any promises, as long as you have the `output` set to something else other than `@com_mojang`.
* Sometimes a file might compile twice in one go.
* Only webp and jpg/jpeg images will be converted to png.
* The output is erased before new files are compiled into it.