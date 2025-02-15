# def add_to_dir(root_dir: Path):
#     files = []
#     tmpdir = _make_temp_dir(root_dir.joinpath("_tmp"))
#     for entry in os.scandir(root_dir):
#         if entry.is_dir():
#             continue
#         else:
#             files.append(entry.name)

#     for file in files:
#         if any(x in file for x in VIDEO_FILE_EXTENSIONS):
#             new_dir = file[:-11]
#             newpath = Path(root_dir + new_dir)
#             src = dst = root_dir.joinpath(file)
#             dst = newpath.joinpath(file)
#             print("Moving: %s to %s" % (src, dst))
#             to_tmp = os.path.join(tmpdir, new_dir)
#             print("Moving: %s to %s" % (newpath, to_tmp))
#             try:
#                 os.mkdir(newpath)
#                 shutil.move(src, dst)
#                 shutil.move(newpath, to_tmp, copy_function=shutil.copytree)
#             except Exception:
#                 print(traceback.format_exc())
#         print("\n")


# def make_config():
#     """TODO
#     For eventual public release.  Make a function that
#     allows the user to generate a config.
#     """
#     config_file = configparser.ConfigParser()
#     config_file.optionxform = str
#     config_file.add_section("paths")
#     paths = ["file_root", "television", "documentaries", "movies", "exit"]
#     while len(paths) > 0:
#         print("Select path to add: ")
#         choice = questions.ask_multichoice(paths)
#         if choice == "exit":
#             # SAVE CONFIG FILE
#             with open(const.PROJECT_ROOT.joinpath("config.ini"), "w") as file_object:
#                 config_file.write(file_object)
#             print("Config file 'config.ini' created")
#             exit()
#         else:
#             path = questions.ask_text_input(f"Enter {choice} path:")
#             config_file["paths"][choice] = path
#             print(f"Adding to config.ini: [paths]:{choice} = {path}")
#             paths.remove(choice)
