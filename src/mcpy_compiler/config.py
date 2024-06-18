import json

def create_config(output:str, auto_manifest:bool, project_name:str, project_description:str, target_version:str, script_entry:str, packs:list, show_compiled:bool, compile_confusing_files:bool, auto_texture_defining:bool, auto_textures_do:list, show_dates:bool):
    """
    Create a config file.

    `output`: where to compile output, use `@com_mojang` to go to mojang folder directly.

    `auto_manifest`: whether to create manifest and dependencies automatically.

    `project_name`: addon display name.

    `project_description`: addon description.

    `target_version`: target minecraft version.

    `script_entry`: where the script entry is, required if used scripts and `auto_manifest`.

    `packs`: what packs are present and/or to compile. `bp`, and/or `rp`.

    `show_compiled`: whether to show files that compiled successfully.

    `compile_confusing_files`: whether to compile files that the compiler can't figure out what to do with. Will compile as bytes most of the time.

    `auto_texture_defining`: whether to generate texture definitions automatically. Texture names will be the filename.

    `auto_textures_do`: what type of texture to automatically define. `blocks`, `items`, and `list`.

    `show_dates`: whether to show the date and time a file compiled at.
    """
    config = {
        "output": output,
        "auto_manifest": auto_manifest,
        "project_name": project_name,
        "project_description": project_description,
        "target_version": target_version,
        "script_entry": script_entry,
        "packs": packs,
        "show_compiled": show_compiled,
        "compile_confusing_files": compile_confusing_files,
        "auto_texture_defining": auto_texture_defining,
        "auto_textures_do": auto_textures_do,
        "show_dates": show_dates
    }

    with open("config.json", "w") as f:
        f.write(json.dumps(config, indent=4))