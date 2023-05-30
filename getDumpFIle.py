import os
import re
from ppadb.client import Client as AdbClient
import subprocess

list_file = [
    # "/system/",
    "/data/data/com.google.android.apps.nexuslauncher/databases/",
    "/data/data/misc/bluedroid/",
    "/data/data/com.android.providers.contacts/databases/",
    "/data/data/com.android.chrome/app_chrome/Default/",
    "/data/data/com.android.providers.contacts/databases/",
    "/data/data/com.google.android.apps.messaging/databases/",
    "/data/data/misc/bootstat/",
    "/data/system/usagestats/0/",
    "/data/system_ce/0/",
    "/data/misc/bluedroid/",
    # "/data/system/build.prop",
    "/data/system/",
    "/data/user_de/0/com.android.providers.telephony/databases/",
    "/data/data/com.google.android.keep/databases/",
    "/data/data/com.google.android.apps.nexuslauncher/databases/",
    # "/data/system/packages.list",
    # "/data/system/packages.xml",
    "/data/misc/bootstat/",
    "/data/system_ce/",
    "/data/data/com.microsoft.teams/databases/",
    "/data/data/com.whatsapp/databases/",
    "/data/data/com.whatsapp/shared_prefs/",
    "/data/data/com.whatsapp/files",
    "/data/misc/wifi/",
    "/data/data/com.google.android.gm/"
]


def create_directory(device, path):
    # Split the path into individual levels
    levels = path.strip("/").split("/")
    print(levels)
    # Create each level of the directory
    current_path = "/"
    for level in levels:
        current_path = f"{current_path}/{level}"
        if level == levels[-1] and device.shell(f"test -f {current_path} && echo 'true'").strip() == "true" :
            print("Breaking guys !")
            break
        device.shell(f"mkdir -p '{current_path}'")

    print("Directory created successfully!")


def copy_files(device, input_path, output_path):
    op = output_path + input_path
    input_path = input_path + "*"
    # print(input_path, op)
    # print(f"su -c cp -R {input_path} {op} \n")

    create_directory(device, op)
    device.shell(f"su -c cp -R {input_path} {op} ")


def rename_folders(device, folder_path):
    # List the contents of the current folder
    con = device.shell(f"ls {folder_path}").strip().split("\n")
    print(len(con))
    for conts in con:
        print(conts)
        contents = conts.split(" ")
        print("contnets -", contents)

        for item in contents:
            item_path = f"{folder_path}/{item}"
            # print("item -", item, type(item), bool(item))
            # if not bool(item):
            #     return
            # rename_folders(device, item_path)

            # Check if the item is a folder
            if device.shell(f"test -d {item_path} && echo 'true'").strip() == "true":
                # print("item -", item, type(item), bool(item))
                if bool(item):
                    rename_folders(device, item_path)
                # Rename the folder if it contains ":"
                if ":" in item:
                    new_item = item.replace(":", "_")
                    new_item_path = f"{folder_path}/{new_item}"

                    # Rename the folder
                    device.shell(f"mv {item_path} {new_item_path}")

                    # Recursively rename folders inside the renamed folder
                    # rename_folders(device, new_item_path)
            # Check if the item is a symbolic link
            elif device.shell(f"test -L {item_path} && echo 'true'").strip() == "true":
                # Get the target path of the symbolic link
                target_path = device.shell(f"readlink {item_path}").strip()

                # Rename the symbolic link if it contains ":"
                if ":" in target_path:
                    new_target = target_path.replace(":", "_")

                    # Update the target of the symbolic link
                    device.shell(f"ln -sf {new_target} {item_path}")

            elif device.shell(f"test -f {item_path} && echo 'true'").strip() == "true":
                # Rename the file if it contains ":"
                if ":" in item:
                    new_item = item.replace(":", "_")
                    # new_item = new_item.replace("@", "_")
                    new_item_path = f"{folder_path}/{new_item}"

                    # Rename the file
                    device.shell(f"mv {item_path} {new_item_path}")



def get_Dump_File():
    # Default is "127.0.0.1" and 5037
    client = AdbClient(host="127.0.0.1", port=5037)
    device = client.device("emulator-5554")
    output_path = "/storage/emulated/0/dumpfile"
    # device.shell(f"mkdir '{output_path}'")


    for input_path in list_file:
        try:
            copy_files(device, input_path, output_path)
        except:
            print("Error in ", input_path)

    rename_folders(device, "/storage/emulated/0/dumpfile/data/data/com.google.android.gm/")
    subprocess.run(["adb", "pull", "/storage/emulated/0/dumpfile", "."])
    device.shell("rm -r /storage/emulated/0/dumpfile/")

    return  "dumpfile"