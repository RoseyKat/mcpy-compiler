import os
import shutil
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import sleep
import cv2
from uuid import uuid4

with open("config.json", "r") as f:
    config = json.loads(f.read())

global save_count
save_count = 0

class fileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global save_count
        save_count += 1
        if event.src_path.startswith(".\\output") == False and event.is_directory == False and save_count == 1:
            single_compile.file(event.src_path)

        # This is used to prevent a file from compiling several times from 1 save
        if save_count >= 2:
            sleep(0.2)
            save_count = 0

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

        if path.endswith(".mcfunction") or path.endswith(".mc"):
            single_compile.mcfunc(path)
        
        elif path.endswith(".json"):
            single_compile.gen_json(path)

        elif path.endswith(".png"):
            single_compile.image(path)

        elif path.endswith(".js") or path.endswith(".ts"):
            single_compile.script(path)

        elif path.endswith(".lang"):
            single_compile.lang(path)

        else:
            print(f"CONFUSING FILE: {path}")

        if config["show_compiled"]:
            print(f"Compiled: {path}")

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
            print(f"ERROR COMPILING: {path}")

    def gen_json(path):
        if path.endswith("manifest.json"):
            sleep(0.15)
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

    def script(path):
        with open(path) as f:
            script = f.read()

        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        with open(f"{single_compile.convert_to_output(path)}", "w") as f:
            f.write(script)

    def image(path):
        os.makedirs(os.path.split(single_compile.convert_to_output(path))[0], exist_ok=True)
        image_file = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        cv2.imwrite(single_compile.convert_to_output(path), image_file)

def generate_manifests():
    # Locate any required dependecies
    has_scripts = False
    script_modules = []
    script_module_versions = []

    try:
        with open("BP/manifest.json", "r") as f:
            manifest = json.loads(f.read())["dependencies"]

        for i in manifest:
            module = i["module_name"]
            version = i["version"]

            script_module_versions += [{"module": module, "ver": version}]
    except:pass

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
        "uuid": str(uuid4()),
        "version": [1, 0, 0]
    }]

    bp_dependencies = []

    bp_header_uuid = str(uuid4())
    rp_header_uuid = str(uuid4())

    if has_scripts:
        bp_manifest_modules += [{
            "type": "script",
            "entry": config["script_entry"],
            "language": "javascript",
            "version": [1, 0, 0],
            "uuid": str(uuid4())
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
                "uuid": str(uuid4()),
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

if config["auto_manifest"]:
    generate_manifests()

iterate_pack("BP")
iterate_pack("RP")

observer = Observer()

observer.schedule(fileChangeHandler(), "./BP", recursive=True)
observer.schedule(fileChangeHandler(), "./RP", recursive=True)

observer.start()
print(f"Watching: {os.getcwd()}")

try:
    while True:
        sleep(0.1)
except:
    observer.stop()

observer.join()