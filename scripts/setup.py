#!/usr/bin/python3

import shlex
import subprocess
import sys
import os
import argparse
import fileinput
from xxlimited import new

# Get directories
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(f"{CURRENT_DIR}/..")

# Directories in wiki container
WIKI_TMP_DIR = "/tmp"
WIKI_BASE_DIR = "/var/www/mediawiki/w"
WIKI_EXTENSIONS_DIR = f"{WIKI_BASE_DIR}/extensions"


def execute_command_in_container(command, container_name):
    try:
        cmd = f"docker exec {container_name} sh -c {shlex.quote(command)}"
        process = subprocess.run(shlex.split(
            cmd), stdout=sys.stdout, stderr=sys.stdout)
        process.check_returncode()

    except subprocess.CalledProcessError as err:
        print(f"Error in command {err.cmd}, error code {err.returncode}")
        sys.exit(err.returncode)


def build_containers(name):
    try:
        docker_build_cmd = f"docker-compose -f {BASE_DIR}/docker-compose.yml -p {name} up -d"

        docker_build_process = subprocess.run(shlex.split(
            docker_build_cmd), stdout=sys.stdout, stderr=sys.stdout)

        docker_build_process.check_returncode()

        print("Docker containers are succesfully built.")
    except subprocess.CalledProcessError as err:
        print(f"Error in command {err.cmd}, error code {err.returncode}")
        sys.exit(err.returncode)


def replace_line_in_file(file_path, old_string, new_line):
    if new_line[-1] != "\n":
        new_line += "\n"
    try:
        with fileinput.input(file_path, inplace=True) as file:
            for line in file:
                line = new_line if old_string in line else line
                sys.stdout.write(line)

    except FileNotFoundError as err:
        sys.exit(f"File: err.filename cannot be found.")


def main(argv=sys.argv[1:]):

    # Parse arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description='Setup the project.')

    parser.add_argument("--default", action="store_true",
                        help="Run the default setup.")

    parser.add_argument("--name", type=str,
                        default="mediawiki", help="Name of the project.")

    parser.add_argument("--enable-uploads", type=bool,
                        default=False, help="Enable uploads to wiki.")

    parser.add_argument(
        "--access", type=str, choices=["open", "account", "restricted", "private"], default="open")

    args = parser.parse_args(argv)

    if args.default:
        print("Error: Default setup not implemented yet.")
        sys.exit(1)

    name_wo_spaces = args.name.strip().replace(" ", "_").lower()

    # Build containers
    build_containers(name_wo_spaces)

    # Wait until database is ready
    wait_db_container_cmd = "until nc -z -v -w30 db 3306; do echo 'Waiting for database'; sleep 2; done"
    execute_command_in_container(
        wait_db_container_cmd, f"{name_wo_spaces}_wiki_1")

    # Setup wiki
    install_mediwiki_container_cmd = f"php {WIKI_BASE_DIR}/maintenance/install.php \
        --dbname wiki_db \
        --dbserver db \
        --dbtype mysql \
        --extensions \
            'CategoryTree, CodeEditor, Math, PdfHandler, VisualEditor, WikiEditor' \
        --dbpass wiki_pw \
        --dbuser wiki_user \
        --lang en \
        --pass defaultpassword \
        --scriptpath /w \
        --skins \
            'MinervaNeue, MonoBook, Timeless, Vector' \
        '{args.name}' \
        Admin"

    execute_command_in_container(
        install_mediwiki_container_cmd, f"{name_wo_spaces}_wiki_1")

    print("Mediawiki is succesfully installed.")

    # Copy LocalSettings.php for configuring
    try:
        copy_local_settings_cmd = f"docker cp \
            {name_wo_spaces}_wiki_1:{WIKI_BASE_DIR}/LocalSettings.php \
            {BASE_DIR}/configs/LocalSettings.php"
        copy_local_settings_process = subprocess.run(shlex.split(
            copy_local_settings_cmd), stdout=sys.stdout, stderr=sys.stdout)
        copy_local_settings_process.check_returncode()

    except subprocess.CalledProcessError as err:
        print(f"Error in command {err.cmd}, error code {err.returncode}")
        sys.exit(err.returncode)

    # Enable uploads
    if args.enable_uploads:
        replace_line_in_file(f"{BASE_DIR}/configs/LocalSettings.php",
                             "$wgEnableUploads", "$wgEnableUploads = true;")
        #     enable_uploads_container_cmd = f"sed -i '/$wgEnableUploads/c\$wgEnableUploads = true;' \
        #         {WIKI_BASE_DIR}/LocalSettings.php"

        #     execute_command_in_container(
        #         enable_uploads_container_cmd, f"{name_wo_spaces}_wiki_1")

        print("Uploads are enabled.")

    local_settings = open(f"{BASE_DIR}/configs/LocalSettings.php", "a")
    # Access control
    if args.access == "account":
        local_settings.writelines(
            ["$wgGroupPermissions['*']['edit'] = false;\n"])

    elif args.access == "restricted":
        local_settings.writelines(
            ["$wgGroupPermissions['*']['createaccount'] = false;\n",
             "$wgGroupPermissions['*']['edit'] = false;\n"])

    elif args.access == "private":
        local_settings.writelines(
            ["$wgGroupPermissions['*']['createaccount'] = false;\n",
             "$wgGroupPermissions['*']['edit'] = false;\n",
             "$wgGroupPermissions['*']['read'] = false;\n"])

    local_settings.close()

    # Copy updated LocalSettings.php back to container
    try:
        copy_local_settings_cmd = f"docker cp \
            {BASE_DIR}/configs/LocalSettings.php \
            {name_wo_spaces}_wiki_1:{WIKI_BASE_DIR}/LocalSettings.php"
        copy_local_settings_process = subprocess.run(shlex.split(
            copy_local_settings_cmd), stdout=sys.stdout, stderr=sys.stdout)
        copy_local_settings_process.check_returncode()

    except subprocess.CalledProcessError as err:
        print(f"Error in command {err.cmd}, error code {err.returncode}")
        sys.exit(err.returncode)
    os.remove(f"{BASE_DIR}/configs/LocalSettings.php")

    print("You can now access the wiki at http://localhost/w/")


if __name__ == "__main__":
    main()
