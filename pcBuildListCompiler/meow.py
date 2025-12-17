import os
#Not necessary for proj just wanted to get the tree for the proj to fix some directory route info

def print_tree(directory, prefix="", is_last=True):
    """Print directory tree structure"""
    basename = os.path.basename(directory)
    connector = "└── " if is_last else "├── "
    print(prefix + connector + basename + "/")

    # Get all items in directory
    try:
        items = sorted(os.listdir(directory))
    except PermissionError:
        return

    # Separate files and folders
    files = [item for item in items if os.path.isfile(os.path.join(directory, item))]
    folders = [item for item in items if os.path.isdir(os.path.join(directory, item))]

    # Update prefix for children
    extension = "    " if is_last else "│   "
    new_prefix = prefix + extension

    # Print folders first
    for i, folder in enumerate(folders):
        is_last_folder = (i == len(folders) - 1) and (len(files) == 0)
        print_tree(os.path.join(directory, folder), new_prefix, is_last_folder)

    # Print files
    for i, file in enumerate(files):
        is_last_file = i == len(files) - 1
        file_connector = "└── " if is_last_file else "├── "
        print(new_prefix + file_connector + file)


# Usage
print_tree(".")