# *************************************************************************************
# CLI Utility used for manage configuration file
# *************************************************************************************
__author__ = "IU1BOW - Corrado"
import os
import os.path
from os import path
import json

configs = [
    ("mycallsign", "Callsign____________________: "),
    ("mysql/host", "MySql host__________________: "),
    ("mysql/db", "MySql database______________: "),
    ("mysql/user", "MySql user__________________: "),
    ("mysql/passwd", "MySql password______________: "),
    ("timer/interval", "Spot page refresh(ms)_______: "),
    ("mail", "Mail address________________: "),
    ("mail_token", "token google 2FA auth_______: "),
    ("telnet/host", "Telnet host_________________: "),
    ("telnet/port", "Telnet port_________________: "),
    ("telnet/user", "Telnet user________________: "),
    ("telnet/password", "Telnet password (optional)_: "),    
    ("enable_cq_filter", "Enable cq filter___________: "),
]


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


TEMPLATE_FILE = "../cfg/config.json.template"
USER_FILE = "../cfg/config.json"
# search and open the configuration file
def get_cfg_file(template):
    if template:
        cfg_file = TEMPLATE_FILE
        if not path.exists(cfg_file):
            print("file not found")
            cfg_file = ""
    else:
        cfg_file = USER_FILE
        if not path.exists(cfg_file):
            cfg_file = TEMPLATE_FILE
            if not path.exists(cfg_file):
                cfg_file = ""

    print("Configuration file loaded from: " + cfg_file)
    return cfg_file


# covert file in json
def get_cfg_json(f):
    if f:
        with open(f) as json_data_file:
            cfg = json.load(json_data_file)
    else:
        cfg = {}

    return cfg


# read a single value from json
def get_cfg_value(cfg, key):

    k_arr = key.split("/")
    l_arr = len(k_arr)

    try:
        if l_arr == 1:
            val = cfg[k_arr[0]]
        elif l_arr == 2:
            val = cfg[k_arr[0]][k_arr[1]]
    except KeyError:
        val = ""

    return val


def set_cfg_value(cfg, key, val):
    k_arr = key.split("/")
    l_arr = len(k_arr)

    try:
        if l_arr == 1:
            cfg[k_arr[0]] = val
        elif l_arr == 2:
            cfg[k_arr[0]][k_arr[1]] = val
    except KeyError:
        pass

    return cfg


def style_field(lbl, val):
    return lbl + bcolors.BOLD + str(val) + bcolors.ENDC


def show_menu(cfg, key):
    menu = get_cfg_value(cfg, "menu/menu_list")
    i = -1
    for element in menu:
        i += 1
        print(
            style_field(str(i) + ". external: ", str(element["external"]))
            + style_field(", label: ", element["label"])
        )
        print(style_field("   link____: ", element["link"]))
        print()
    return


def help_list():
    print()
    print("   h:  help")
    print("   vc: view config.")
    print("   ec: edit config.")
    print("   vm: view menu")
    print("   em: edit menu")
    print("   s:  save")
    print("   t:  load config. from template")
    print()
    print("   x:  exit")
    print()
    return


def help_menu_edit():
    print()
    print("   n:  new menu entry")
    print("   d:  delete menu entry")
    print("   e:  edit menu entry")
    print()
    print("   x:  exit")
    print()
    return


def view(cfg, t):
    if t == "c":
        i = 0
        for element in configs:
            (key, lbl) = element
            print(style_field(str(i) + ". " + lbl, str(get_cfg_value(cfg, key))))
            i += 1
    elif t == "m":
        print("Menu:")
        show_menu(cfg, "menu/menu_list")

    print()
    return


def user_input(caption):
    return input(caption)


def edit_config(cfg):
    view(cfg, "c")
    inp = ""
    while inp != "x":
        inp = str(
            user_input("Type the number of config. you would to edit, x for end: ")
        ).lower()
        if inp.isdigit():
            inp = int(inp)
            try:
                (key, lbl) = configs[inp]
                print(style_field(lbl, get_cfg_value(cfg, key)))
                val = str(user_input("Enter new value, [ENTER] for nothing: "))
            except IndexError:
                print("configuration not found!")
            finally:
                if val != "x" and val != "":
                    cfg = set_cfg_value(cfg, key, val)

    return cfg


def menu_delete_entry(cfg):
    view(cfg, "m")
    inp = ""
    while inp != "x":
        inp = str(
            user_input("Choose the menu you would to delete, x for end: ")
        ).lower()
        if inp.isdigit():
            inp = int(inp)
            element = cfg["menu"]["menu_list"]
            try:
                del element[inp]
                cfg["menu"]["menu_list"] = element
            except IndexError:
                print("menu entry not found!")

    return cfg


def is_external(val):
    return val == "y"


def menu_input_entry(entry, new_entry):
    if not new_entry:
        print("label old value: " + entry["label"])

    label = str(user_input("label new value: "))
    if not new_entry:
        print("link old value: " + entry["link"])

    link = str(user_input("link value: "))
    if not new_entry:
        print("external old value: " + str(entry["external"]))

    external = ""
    while external != "y" and external != "n":
        external = str(user_input("open link external [y/n]: ")).lower()

    external = is_external(external)

    entry["label"] = label
    entry["link"] = link
    entry["external"] = external

    return entry


def menu_edit_entry(cfg):
    view(cfg, "m")
    inp = ""
    while inp != "x":
        inp = str(user_input("Choose the menu you would to edit, X for end: ")).lower()
        if inp.isdigit():
            inp = int(inp)
            element = cfg["menu"]["menu_list"]
            try:
                element[inp] = menu_input_entry(element[inp], False)
                cfg["menu"]["menu_list"] = element
            except IndexError:
                print("menu entry not found!")

    return cfg


def menu_new_entry(cfg):
    view(cfg, "m")
    inp = ""
    valid = False
    entry = menu_input_entry({"label": "", "link": "", "external": False}, True)
    while not valid:
        inp = str(
            user_input("Enter the position number of your menu entry, X for end: ")
        )
        if inp.isdigit():
            inp = int(inp)
            if inp > len(cfg["menu"]["menu_list"]):
                print("position not valid!")
                valid = False
            elif inp == len(cfg["menu"]["menu_list"]):
                cfg["menu"]["menu_list"].append(entry)
                valid = True
            else:
                cfg["menu"]["menu_list"].insert(inp, entry)
                valid = True
        else:
            valid = False

    return cfg


def edit_menu(cfg):
    view(cfg, "m")
    inp = ""
    while inp != "x":
        help_menu_edit()
        inp = str(user_input("Edit menu> make your choiche: ")).lower()
        if inp == "n":
            cfg = menu_new_entry(cfg)
        elif inp == "d":
            cfg = menu_delete_entry(cfg)
        elif inp == "e":
            cfg = menu_edit_entry(cfg)

    return cfg


def save_cfg(cfg):
    with open(USER_FILE, "w") as outfile:
        json.dump(cfg, outfile, indent=4)
    print("configuration saved to: " + USER_FILE)
    return


def main():
    print()
    print("*** DxSpider configuration ***")
    finput = get_cfg_file(False)
    help_list()
    cfg = get_cfg_json(finput)
    inp = ""
    while inp != "x" and inp != "exit":
        inp = str(user_input("Main> make your choiche: ")).lower()
        if inp == "h" or inp == "?" or inp == "help":
            help_list()
        elif inp == "vc":
            view(cfg, "c")
        elif inp == "vm":
            view(cfg, "m")
        elif inp == "ec":
            cfg = edit_config(cfg)
        elif inp == "em":
            cfg = edit_menu(cfg)
        elif inp == "s" or inp == "save":
            save_cfg(cfg)
        elif inp == "t":
            finput = get_cfg_file(True)
            cfg = get_cfg_json(finput)


if __name__ == "__main__":
    main()
