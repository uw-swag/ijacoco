import os
import re

import seutil as su

logger = su.log.get_logger(__name__)

def remove_java_files(tests_to_exclude):
    for root, dirs, files in os.walk("src/test"):
        for file_name in files:
            if file_name.endswith(tuple(tests_to_exclude)):
                file_path = os.path.join(root, file_name)
                os.remove(file_path)
                logger.info(f"Removed: {file_path}")

def save_reports(data_directory, project_directory, coverage_choice, version, suffix):
    # Create the destination folder if it doesn't exist
    destination_folder = f"{data_directory}/_log_{suffix}/{version}"
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        # logger.info(f"Make directory {destination_folder}.")

    # Copy the source folder to the destination folder
    coverage_repo_folder= f"{project_directory}/coverage-reports"
    surefire_repo_foler = f"{project_directory}/target/surefire-reports"
    ekstazi_repo_folder = f"{project_directory}/.ekstazi"
    if coverage_choice in ["ijacoco", "ekstazi"]:
        su.bash.run(f"cp -r {ekstazi_repo_folder} {destination_folder}", check_returncode=0)
    if coverage_choice in ["ijacoco", "bjacoco"]:
        su.bash.run(f"cp -r {coverage_repo_folder} {destination_folder}", check_returncode=0)
    su.bash.run(f"cp -r {surefire_repo_foler} {destination_folder}", check_returncode=0)
    logger.info("Folders copied.")