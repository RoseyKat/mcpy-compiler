import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import cv2
from uuid import uuid4
import datetime

with open("config.json", "r") as f:
    config = json.loads(f.read())

item_texture = {"resource_pack_name": config["project_name"], "texture_data": {}}
terrain_texture = {"resource_pack_name": config["project_name"], "num_mip_levels": 0, "padding": 0, "texture_data": {}}
texture_list = []
warnings = []
compile_count = 0

class fileChangeHandler(FileSystemEventHandler):
    def check_do_compile(path:str):
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
    def get_filetype(path:str):
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
    # The json library can't handle comments so gotta remove them :3 :3 :3 :3 >:(
    def remove_json_comments(path):
        with open(f"{path}", "r") as f:
            file = f.read()

        updated_text = ""

        keep_moving = True
        for i in file:
            if i == "/":
                keep_moving = False

            if keep_moving == False and i == "\n":
                keep_moving = True

            if keep_moving:
                updated_text += i

        return updated_text

    def file(path:str):
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
        if path.startswith("BP"):
            if config["output"] == "@com_mojang":
                return path.replace("BP", os.path.expanduser(f"~/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/development_behavior_packs/{config["project_name"]} BP"))
            
            else:
                return path.replace("BP", f"{config["output"]}/BP")
        
        elif path.startswith("RP"):
            if config["output"] == "@com_mojang":
                return path.replace("RP", os.path.expanduser(f"~/AppData/Local/Packages/Microsoft.MinecraftUWP_8wekyb3d8bbwe/LocalState/games/com.mojang/development_resource_packs/{config["project_name"]} RP"))
            
            else:
                return path.replace("RP", f"{config["output"]}/RP")
    
    def lang(path):
        with open(f"{path}", "r") as f:
            lang_file = f.readlines()

        write_lang = ""

        for i in lang_file:
            if i != "\n" and i.startswith("##") == False:
                write_lang += f"{i}"

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "w") as f:
            f.write(write_lang)

    def mcfunc(path):
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

            if str(path).endswith(".mc"):
                path = path.replace(".mc", ".mcfunction")
            os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
            with open(f"{single_compile.convert_to_output(path)}", "w") as f:
                f.write(write_function)

        except:
            warnings.append(f"ERROR COMPILING: {path}")

    def gen_json(path):
        try:
            if path.endswith("manifest.json"):
                time.sleep(0.15)
            try:
                with open(f"{path}", "r") as f:
                    json_file = json.loads(f.read())

            except:
                commentless_json = single_compile.remove_json_comments(path)
                json_file = json.loads(commentless_json)
                del commentless_json

            os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
            with open(f"{single_compile.convert_to_output(path)}", "w") as f:
                f.write(json.dumps(json_file))
        except json.JSONDecodeError as error:
            if str(error) == "Expecting value: line 1 column 1 (char 0)":
                warnings.append(f"WARNING: Empty json file: {path}")
            else:
                raise
            

    def script(path):
        with open(path) as f:
            script = f.read()

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "w") as f:
            f.write(script)

    def image(path:str):
        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)

        ext = os.path.splitext(path)[1]

        image_file = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(single_compile.convert_to_output(path.replace(ext, ".png")), image_file)

    def byte_file(path):
        with open(f"{path}", "rb") as f:
            file = f.read()

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "wb") as f:
            f.write(file)

def generate_manifests():
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

def iterate_pack(path):
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

            single_compile.file(filepath)

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

starting_time = round(time.time() * 1000)

if config["auto_manifest"]:
    generate_manifests()

if "bp" in config["packs"]:
    iterate_pack("BP")
if "rp" in config["packs"]:
    iterate_pack("RP")

if config["auto_texture_defining"]:
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

for i in warnings:
    print(i)

print(f"Compiled {compile_count} files in: {str(starting_time - finishing_time).replace("-", "")}ms")

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