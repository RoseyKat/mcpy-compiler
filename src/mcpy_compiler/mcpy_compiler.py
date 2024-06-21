"""mcpy-compiler"""
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import cv2
from uuid import uuid4
import datetime
import shutil
import requests

output_override = None
watch_ran = False
texture_list = []
warnings = []
compile_count = 0

class mcpy_error(Exception):
    def __init__(self, message):
        self.message = message
        super(mcpy_error, self).__init__(message)

try:
    with open("config.json", "r") as f:
        config = json.loads(f.read())
        try:
            config["output"]
        except:
            mcpy_error("config: output is missing!")
            exit()

        if "auto_manifest" not in config:
            config["auto_manifest"] = False

        if "project_name" not in config:
            raise mcpy_error("config: project name is missing!")
        
        if "project_description" not in config:
            config["project_description"] = config["project_description"]
            warnings.append("WARNING: project description in config was not found, defaulted to project name!")

        if "target_version" not in config:
            latest = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()["latest"]["release"]

            if len(latest.split(".")) == 2:
                latest = f"{latest}.0"

            config["target_version"] = latest
            warnings.append("WARNING: target version not found in config, defaulted to latest minecraft version!")

        if "script_entry" not in config:
            config["script_entry"] = None

        if "packs" not in config:
            raise mcpy_error("config: missing packs")
        
        if "show_compiled" not in config:
            config["show_compiled"] = True

        if "compile_confusing_files" not in config:
            config["compile_confusing_files"] = False

        if "auto_texture_defining" not in config:
            config["auto_texture_defining"] = False

        if "auto_textures_do" not in config:
            config["auto_textures_do"] = []

        if "show_dates" not in config:
            config["show_dates"] = False

        if "use_searcher" not in config:
            config["use_searcher"] = False
except:
    raise mcpy_error("No config!")

try:
    with open("searcher.json", "rb") as f:
        searcher = json.loads(f.read())
except: searcher = None

item_texture = {"resource_pack_name": config["project_name"], "texture_data": {}}
terrain_texture = {"resource_pack_name": config["project_name"], "num_mip_levels": 0, "padding": 0, "texture_data": {}}

class fileChangeHandler(FileSystemEventHandler):
    """Watchdog"""
    def check_do_compile(path:str):
        """Check if file should actually be compiled\n\n`path` must be `BP` or `RP`, and also be in configs packs"""
        if path.startswith("./BP") and "bp" in config["packs"]:
            single_compile.file(path)
        elif path.startswith("./RP") and "rp" in config["packs"]:
            single_compile.file(path)

    def on_modified(self, event):
        if event.is_directory == False:
            fileChangeHandler.check_do_compile(event.src_path)

    def on_created(self, event):
        if event.is_directory == False:
            fileChangeHandler.check_do_compile(event.src_path)

    def on_deleted(self, event):
        if event.is_directory == False:
            single_compile.remove_file(event.src_path)

class compiler_tools:
    """Some useful tools for commonly used cases"""
    def get_filetype(path:str):
        """Returns type of file in minecraft terms\n\nReturns `None` if `path` has no valid/known filetype"""
        ext = os.path.splitext(path)[1]

        match ext:
            case ".png":
                return "image"
            case ".jpeg":
                return "image"
            case ".jpg":
                return "image"
            case ".webp":
                return "image"
            case ".mc":
                return "function"
            case ".mcfunction":
                return "function"
            case ".json":
                return "json"
            case ".js":
                return "script"
            case ".ts":
                return "script"
            case ".lang":
                return "language"
            case ".ogg":
                return "sound"
        return None

class single_compile:
    """Class for compiling singular files"""
    # The json library can't handle comments so gotta remove them :3 :3 :3 :3 >:(
    def remove_json_comments(path):
        """Returns string of a valid json object without any comments"""
        with open(f"{path}", "r") as f:
            file = f.readlines()

        updated_text = ""

        for i in file:
            if i.strip().startswith("//") == False:
                updated_text += i

        return updated_text

    def file(path:str):
        """Compile any file. Automatically figures out what type of file it is and calls correct compile function."""
        path = path.replace("\\", "/")
        path = path.replace("./", "")

        global compile_count
        compile_count += 1

        filetype = os.path.splitext(path)[1]
        file_success = False

        match filetype:
            case ".mc":
                file_success = True
                single_compile.mcfunc(path)
            case ".mcfunction":
                file_success = True
                single_compile.mcfunc(path)
            case ".json":
                file_success = True
                if path.startswith("BP/items") or path.startswith("BP/blocks") or path.startswith("BP/entities"):
                    single_compile.bp_json(path)
                else:
                    single_compile.gen_json(path)
            case ".png":
                file_success = True
                single_compile.image(path)
            case ".jpeg":
                file_success = True
                single_compile.image(path)
            case ".jpg":
                file_success = True
                single_compile.image(path)
            case ".webp":
                file_success = True
                single_compile.image(path)
            case ".lang":
                file_success = True
                single_compile.lang(path)
            case ".js":
                file_success = True
                single_compile.script(path)
            case ".ts":
                file_success = True
                single_compile.script(path)
            case ".ogg":
                file_success = True
                single_compile.byte_file(path)

        if file_success == False and config["compile_confusing_files"] == False:
            compile_count -= 1
            warnings.append(f"CONFUSING FILE: {path}")

        elif config["compile_confusing_files"]:
            single_compile.byte_file(path)

        if config["show_compiled"]:
            if config["show_dates"]:
                print(f"{datetime.datetime.today()}: Compiled: {path}")
            else:
                print(f"Compiled: {path}")

    def remove_file(path:str):
        """Delete a file if it `path` parent is also in configs packs"""
        path = path.replace("\\", "/")
        path = path.replace("./", "")

        if path.endswith(".mc"):
            path = path.replace(".mc", ".mcfunction")

        if path.startswith("BP") and "bp" in config["packs"]:
            os.remove(single_compile.convert_to_output(path))
            print(f"Removed file: {path}")

        elif path.startswith("RP") and "rp" in config["packs"]:
            os.remove(single_compile.convert_to_output(path))
            print(f"Removed file: {path}")

    def convert_to_output(path:str):
        """Convert `path` to configs output. If output is `@com_mojang` then returns packs development directory"""
        global output_override
        if path.startswith("BP"):
            if config["output"] == "@com_mojang" and output_override == None:
                return path.replace("BP", os.path.expanduser(f"~/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/development_behavior_packs/{config["project_name"]} BP"))
            
            elif output_override != None:
                return path.replace("BP", f"{output_override}/BP")
            
            else:
                return path.replace("BP", f"{config["output"]}/BP")
        
        elif path.startswith("RP"):
            if config["output"] == "@com_mojang" and output_override == None:
                return path.replace("RP", os.path.expanduser(f"~/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/development_resource_packs/{config["project_name"]} RP"))
            
            elif output_override != None:
                return path.replace("RP", f"{output_override}/RP")
            
            else:
                return path.replace("RP", f"{config["output"]}/RP")
    
    def run_searcher(s:str, path:str):
        """Replace ``s`` string with the searcher keys."""
        if searcher is not None:
            run_replace = [False, False]
            for i in searcher:
                if "file_types" in i:
                    for j in i["file_types"]:
                        if "startswith" in j:
                            if path.startswith(j["startswith"]):
                                run_replace[0] = True

                        else:
                            run_replace[0] = True
                        
                        if "endswith" in j:
                            if path.endswith(j["endswith"]):
                                run_replace[1] = True

                        else:
                            run_replace[1] = True

                    if run_replace[0] and run_replace[1]:
                        run_replace = True
                    else:
                        run_replace = False

                else:
                    run_replace = True

                if run_replace:
                    s = s.replace(i["search"], i["replace_with"])
        return s

    def lang(path):
        """Compile a language file, removes lines with comments, and blank lines"""
        with open(f"{path}", "r") as f:
            lang_file = f.readlines()

        write_lang = ""

        for i in lang_file:
            if i != "\n" and i.startswith("##") == False:
                write_lang += f"{i}"

        if config["use_searcher"]:
            write_lang = single_compile.run_searcher(write_lang, path)

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "w") as f:
            f.write(write_lang)

    def mcfunc(path):
        """Compile an mcfunction, removes lines with comments, and blank lines"""
        try:
            try:
                with open(f"{path}", "r") as f:
                    functions = f.readlines()
            except:
                with open(f"{path}", "rb") as f:
                    functions = f.readlines()

                idx = -1
                for i in functions:
                    idx += 1
                    functions[idx] = str(functions[idx]).replace("'", "").replace("b", "", 1)

            write_function = ""

            for i in functions:
                if i != "\n" and i.startswith("#") == False:
                    write_function += f"{i}"

            if config["use_searcher"]:
                write_function = single_compile.run_searcher(write_function, path)

            if str(path).endswith(".mc"):
                path = path.replace(".mc", ".mcfunction")
            os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
            with open(f"{single_compile.convert_to_output(path)}", "w") as f:
                f.write(write_function)

        except:
            warnings.append(f"ERROR COMPILING: {path}")

    def gen_json(path):
        """Compile generic json, output will have removed comments"""
        try:
            # Read file
            with open(f"{path}", "rb") as f:
                compiler_flag = f.readline().decode("utf-8").rstrip()
                try:
                    raw_contents = f"{{{f.read().decode("utf-8", "ignore")}"
                except:
                    warnings.append(f"WARNING: `{path}` cannot read raw contents. A compiler flag may be required!")

            # Act upon compiler flags
            if compiler_flag == "//BYTE":
                single_compile.byte_file(path)
            else:
                # Try to load json
                try:
                    json_file = json.loads(raw_contents)

                # Retry without potential comments
                except:
                    commentless_json = single_compile.remove_json_comments(path)
                    json_file = json.loads(commentless_json)
                    del commentless_json

                # Dump and set emojis
                dumped_json = json.dumps(json_file)
                if config["use_searcher"]:
                    dumped_json = str(single_compile.run_searcher(dumped_json, path))

                # Write to output
                os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
                with open(f"{single_compile.convert_to_output(path)}", "w", encoding="utf-8") as f:
                    f.write(dumped_json)
                    
        except json.JSONDecodeError as error:
            if str(error) == "Expecting value: line 1 column 1 (char 0)":
                warnings.append(f"WARNING: Empty json file: {path}")
            else:
                raise

    def bp_json(path:str):
        """Compiles items, blocks, and entities in behavior pack.\n\nPrimary use case is removing the slash at queue_command event"""
        try:
            # Read file
            with open(f"{path}", "rb") as f:
                compiler_flag = f.readline().decode("utf-8").rstrip()
                try:
                    raw_contents = f"{{{f.read().decode("utf-8", "ignore")}"
                except:
                    warnings.append(f"WARNING: `{path}` cannot read raw contents. A compiler flag may be required!")

            # Act upon compiler flags
            if compiler_flag == "//BYTE":
                single_compile.byte_file(path)
            elif compiler_flag == "//PASS":
                pass
            else:
                # Try to load json
                try:
                    json_file = json.loads(raw_contents)

                # Retry without potential comments
                except:
                    commentless_json = single_compile.remove_json_comments(path)
                    json_file = json.loads(commentless_json)
                    del commentless_json
                
                dumped_json = json.dumps(json_file).replace("('", "$>BRACKET").replace("')", "$<BRACKET").replace("\"/", "\"").replace("'/", "\"")

                if config["use_searcher"]:
                    dumped_json = str(single_compile.run_searcher(dumped_json, path))

                os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
                with open(f"{single_compile.convert_to_output(path)}", "w", encoding="utf-8") as f:
                    f.write(dumped_json.replace("$>BRACKET", "('").replace("$<BRACKET", "')"))
                    
        except json.JSONDecodeError as error:
            if str(error) == "Expecting value: line 1 column 1 (char 0)":
                warnings.append(f"WARNING: Empty json file: {path}")
            else:
                raise
            
    def script(path):
        """Compile script file"""
        with open(path) as f:
            script = f.read()

        if config["use_searcher"]:
            script = single_compile.run_searcher(script, path)

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "w") as f:
            f.write(script)

    def image(path:str):
        """Compile an image using `cv2`, will also convert jpeg/jpg/webp to png"""
        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)

        ext = os.path.splitext(path)[1]

        image_file = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(single_compile.convert_to_output(path.replace(ext, ".png")), image_file)

    def byte_file(path):
        """Compile file by reading and writing it as bytes, does no fancy thing.\n\nMain use case scenarios:\n* Audio\n* Unkown files\n* Some unicode characters"""
        with open(f"{path}", "rb") as f:
            file = f.read()

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "wb") as f:
            f.write(file)

def generate_manifests():
    """Generates a manifest based on project name, description, script imports, and packs"""
    # Locate any required dependecies
    has_scripts = False
    script_modules = []
    script_module_versions = []
    script_uuid = False

    try:
        with open("BP/manifest.json", "r") as f:
            manifest = json.loads(f.read())
            dependencies = manifest["dependencies"]

        bp_header_uuid = manifest["header"]["uuid"]
        bp_module_uuid = manifest["modules"][0]["uuid"]
        script_uuid = manifest["modules"][1]["uuid"]

        for i in dependencies:
            module = i["module_name"]
            version = i["version"]

            script_module_versions += [{"module": module, "ver": version}]
    except:
        bp_header_uuid = str(uuid4())
        bp_module_uuid = str(uuid4())
    
    try:
        with open("RP/manifest.json", "r") as f:
            manifest = json.loads(f.read())

        rp_header_uuid = manifest["header"]["uuid"]
        rp_module_uuid = manifest["modules"][0]["uuid"]
    except:
        rp_header_uuid = str(uuid4())
        rp_module_uuid = str(uuid4())

    def add_to_modules(module):
        if module not in script_modules:
            script_modules.append(module)

    if os.path.exists("BP/scripts"):
        has_scripts = True
        for i in os.listdir("BP/scripts"):
            with open(f"BP/scripts/{i}", "r") as f:
                contents = f.read()
                if "@minecraft/server" in contents:
                    add_to_modules("@minecraft/server")

                if "@minecraft/server-gametest" in contents:
                    add_to_modules("@minecraft/server-gametest")

                if ("@minecraft/server-ui") in contents:
                    add_to_modules("@minecraft/server-ui")

    bp_manifest_modules = [{
        "type": "data",
        "uuid": bp_module_uuid,
        "version": [1, 0, 0]
    }]

    bp_dependencies = []

    if has_scripts:
        if script_uuid == False:
            script_uuid = str(uuid4())
        bp_manifest_modules += [{
            "type": "script",
            "entry": config["script_entry"],
            "language": "javascript",
            "version": [1, 0, 0],
            "uuid": script_uuid
        }]

        for i in script_modules:
            use_ver = 0
            for j in script_module_versions:
                if i == j["module"]:
                    use_ver = j["ver"]
                    break

            if use_ver == 0:
                use_ver = str(input(f"Version for module {i}: "))
            bp_dependencies += [{
                "module_name": i,
                "version": use_ver
            }]

    else:
        if "rp" in config["packs"]:
            bp_dependencies += [{
                "uuid": rp_header_uuid,
                "version": [1, 0, 0]
            }]

    eng_ver = str(config["target_version"]).split(".")
    idx = -1
    for i in eng_ver:
        idx += 1
        eng_ver[idx] = int(eng_ver[idx])

    bp_manifest = {
        "format_version": 2,
        "header": {
            "name": config["project_name"],
            "description": config["project_description"],
            "version": [1, 0, 0],
            "min_engine_version": eng_ver,
            "uuid": bp_header_uuid
        },
        "modules": bp_manifest_modules,
        "dependencies": bp_dependencies
    }

    rp_manifest = {
        "format_version": 2,
        "header": {
            "name": config["project_name"],
            "description": config["project_description"],
            "version": [1, 0, 0],
            "min_engine_version": eng_ver,
            "uuid": rp_header_uuid
        },
        "modules": [
            {
                "type": "resources",
                "uuid": rp_module_uuid,
                "version": [1, 0, 0]
            }
        ],
        "dependencies": [
            {
                "uuid": bp_header_uuid,
                "version": [1, 0, 0]
            }
        ]
    }

    if "bp" in config["packs"]:
        with open("BP/manifest.json", "w") as f:
            f.write(json.dumps(bp_manifest, indent=4))

    if "rp" in config["packs"]:
        with open("RP/manifest.json", "w") as f:
            f.write(json.dumps(rp_manifest, indent=4))

def iterate_pack(path, foreachfile=None):
    """Walks through all files using `os.walk` and compiles them.\n\n`path` should be `BP` or `RP`\n\n\nif `foreachfile` is a function, then it will call the function with the filepath as the parameter."""
    for folder, current_folder, files in os.walk(single_compile.convert_to_output(path)):
        for file in files:
            filepath = str(folder + os.sep + file)
            filepath = filepath.replace("\\", "/")

            try:
                os.remove(filepath)
            except:
                pass

    for folder, current_folder, files in os.walk(path):
        for file in files:
            filepath = str(folder + os.sep + file)
            filepath = filepath.replace("\\", "/")

            if foreachfile is None:
                single_compile.file(filepath)

            if foreachfile is not None:
                foreachfile(filepath)

            if path == "RP" and config["auto_texture_defining"]:
                if filepath.startswith("RP/textures/items") and "items" in config["auto_textures_do"] and compiler_tools.get_filetype(filepath) == "image":
                    texture_type = "item"
                elif filepath.startswith("RP/textures/blocks") and "blocks" in config["auto_textures_do"] and compiler_tools.get_filetype(filepath) == "image":
                    texture_type = "block"
                else:
                    texture_type = None

                ext = os.path.splitext(filepath)[1]

                match texture_type:
                    case "item":
                        global item_texture
                        item_texture["texture_data"].update(({f"{os.path.split(filepath)[1].replace(ext, "")}": {"textures": filepath.replace("RP/", "").replace(ext, "")}}))
                    case "block":
                        global terrain_texture
                        terrain_texture["texture_data"].update(({f"{os.path.split(filepath)[1].replace(ext, "")}": {"textures": filepath.replace("RP/", "").replace(ext, "")}}))

                if filepath.startswith("RP/textures") and "list" in config["auto_textures_do"] and compiler_tools.get_filetype(filepath) == "image":
                    global texture_list
                    texture_list.append(f"{filepath.replace("RP/", "").replace(ext, "")}")

def build(addon:bool, splitpacks:bool):
    """Build your project into production.\n\nif `addon` is `True` then it will build a `.mcaddoon` file.\n\nif `splitpacks` is `True` then it will build the RP and BP (if present) mcpacks seperately."""

    global output_override
    output_override = "builds/packs"

    shutil.rmtree("builds/packs", True)

    os.makedirs("builds/packs")

    if "bp" in config["packs"]:
        iterate_pack("BP")
        os.rename("builds/packs/BP", f"builds/packs/{config["project_name"]} BP")
    if "rp" in config["packs"]:
        iterate_pack("RP")
        os.rename("builds/packs/RP", f"builds/packs/{config["project_name"]} RP")

    if addon:
        shutil.make_archive(f"builds/{config["project_name"]}", "zip", "builds/packs")
        with open(f"builds/{config["project_name"]}.zip", "rb") as f:
            file = f.read()
        with open(f"builds/{config["project_name"]}.mcaddon", "wb") as f:
            f.write(file)

    if splitpacks:
        if "bp" in config["packs"]:
            shutil.make_archive(f"builds/{config["project_name"]} BP", "zip", f"builds/packs/{config["project_name"]} BP")
            with open(f"builds/{config["project_name"]} BP.zip", "rb") as f:
                file = f.read()
            with open(f"builds/{config["project_name"]} BP.mcpack", "wb") as f:
                f.write(file)
        
        if "rp" in config["packs"]:
            shutil.make_archive(f"builds/{config["project_name"]} RP", "zip", f"builds/packs/{config["project_name"]} RP")
            with open(f"builds/{config["project_name"]} RP.zip", "rb") as f:
                file = f.read()
            with open(f"builds/{config["project_name"]} RP.mcpack", "wb") as f:
                f.write(file)

    output_override = None



def start_watch():
    """Start watching for file changes"""
    global watch_ran
    watch_ran = True
    observer = Observer()

    observer.schedule(fileChangeHandler(), "./BP", recursive=True)
    observer.schedule(fileChangeHandler(), "./RP", recursive=True)

    observer.start()
    print(f"Watching: {os.getcwd()}")

    try:
        while True:
            time.sleep(0.1)
    except:
        observer.stop()

    observer.join()

def run():
    """Start the compiler\n\nDeletes every file in output then compiles every file and then starts watchdog observer."""
    if watch_ran:
        print("Cannot run if `start_watch` was already ran!")
    else:
        starting_time = round(time.time() * 1000)

        if config["auto_manifest"]:
            generate_manifests()

        if "bp" in config["packs"]:
            iterate_pack("BP")
        if "rp" in config["packs"]:
            iterate_pack("RP")

        if config["auto_texture_defining"] and "rp" in config["packs"]:
            if "items" in config["auto_textures_do"]:
                with open("RP/textures/item_texture.json", "w") as f:
                    f.write(json.dumps(item_texture, indent=4))

                single_compile.gen_json("RP/textures/item_texture.json")

            if "blocks" in config["auto_textures_do"]:
                with open("RP/textures/terrain_texture.json", "w") as f:
                    f.write(json.dumps(terrain_texture, indent=4))

                single_compile.gen_json("RP/textures/terrain_texture.json")

            if "list" in config["auto_textures_do"]:
                with open("RP/textures/texture_list.json", "w") as f:
                    f.write(json.dumps(texture_list, indent=4))

                single_compile.gen_json("RP/textures/texture_list.json")

        finishing_time = round(time.time() * 1000)

        global warnings
        for i in warnings:
            print(i)

        print(f"Compiled {compile_count} files in: {str(starting_time - finishing_time).replace("-", "")}ms")

        observer = Observer()

        if "bp" in config["packs"]:
            observer.schedule(fileChangeHandler(), "./BP", recursive=True)
        if "rp" in config["packs"]:
            observer.schedule(fileChangeHandler(), "./RP", recursive=True)

        observer.start()
        print(f"Watching: {os.getcwd()}")

        try:
            while True:
                time.sleep(0.1)
        except:
            observer.stop()

        observer.join()