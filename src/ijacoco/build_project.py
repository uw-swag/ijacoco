import collections
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import seutil as su
from jsonargparse import CLI

from ijacoco.config_helper import remove_java_files, save_reports
from ijacoco.maven_utils import check_jacoco_exists, pom_add_profile, update_pom_config
from ijacoco.plot_and_read_coverage import (
    calculate_average,
    read_coverage,
)

logger = su.log.get_logger(__name__)


class ProjectBuilder:
    def __init__(
        self, work_dir: Optional[su.arg.RPath] = None, debug_ekstazi: bool = False, debug_ijacoco: bool = False
    ):
        self.proj_dir = Path(__file__).parent.parent.parent
        self.work_dir = work_dir if work_dir is not None else self.proj_dir / "_work"
        self.debug_ekstazi = debug_ekstazi
        self.debug_ijacoco = debug_ijacoco
        self.ensure_ijacoco_bjacoco()

    def ensure_ijacoco_bjacoco(self):
        if not (Path.home() / ".m2/repository/org/ijacoco/ijacoco-maven-plugin").exists():
            logger.info("Maven installing ijacoco...")
            with su.io.cd(self.proj_dir / "ijacoco"):
                su.bash.run("mvn clean install", check_returncode=0)
        if not (Path.home() / ".m2/repository/org/bjacoco/bjacoco-maven-plugin").exists():
            logger.info("Maven installing bjacoco...")
            with su.io.cd(self.proj_dir / "bjacoco"):
                su.bash.run("mvn clean install", check_returncode=0)

    # Config the ppom.xml or exclude tests for running expeirments as listed in projects_config.json
    def pom_config(self, project: str, version: str):
        # load projects that need special configurations
        project_config_file = self.work_dir / "projects/projects_config.json"
        project_config_list = su.io.load(project_config_file)

        for config in project_config_list:
            # check if the project needs special configurations on POM
            if config.get("name") == project:
                if "pom_config" in config and version in config.get("versions"):
                    logger.info(f"Special config on POM for version {version}")
                    type = config["pom_config"]["type"]
                    content = config["pom_config"]["content"]
                    update_pom_config(type, content)

                # check if the project needs special configurations on excluding tests
                if "exclude_tests" in config:
                    logger.info("Need to exclude tests.")
                    exclude_tests = config["exclude_tests"]
                    remove_java_files(exclude_tests)
                break

    # checkout versions in the project
    def checkout_versions(self, commit_hash: str):
        su.bash.run("git stash", check_returncode=0)
        su.bash.run(f"git checkout {commit_hash}", check_returncode=0)
        logger.info(f"Successfully checked out commit {commit_hash}.")

    # run test on the projects with different profile selected
    def run_maven_project(self, project: str, profile: Optional[str] = ""):
        if profile in ["ijacoco", "bjacoco", "ekstazi"]:
            profile = f"-P {profile}p"
        else:
            profile = "-P retestallp"

        start = time.time()

        # load projects that need special configurations
        project_config_file = self.work_dir / "projects/projects_config.json"
        project_config_list = su.io.load(project_config_file)

        # -fn is used to ignore test failures
        skips = "-fn -Dgpg.skip -Djacoco.skip -Dcheckstyle.skip -Drat.skip -Denforcer.skip -Danimal.sniffer.skip"
        "-Dmaven.javadoc.skip -Dfindbugs.skip -Dwarbucks.skip -Dmodernizer.skip -Dimpsort.skip -Dpmd.skip"
        "-Dxjc.skip -Dair.check.skip-all"

        maven_command = f"mvn clean test {skips} {profile}"

        # check if the project needs special configurations on maven command
        for config in project_config_list:
            if config.get("name") == project and "mvn_command" in config:
                logger.info("Special config on maven command.")
                maven_command = f"{config.get('mvn_command')} {skips} {profile}"
                break

        if self.debug_ekstazi:
            su.io.dump(Path.cwd() / ".rtsrc", "debug=true\ndebug.mode=everywhere\n", su.io.fmts.txt)
        else:
            su.io.rm(Path.cwd() / ".rtsrc")

        if self.debug_ijacoco:
            su.io.dump(Path.cwd() / ".ijacocorc", "debug=true\ndebug.mode=everywhere", su.io.fmts.txt)
        else:
            su.io.rm(Path.cwd() / ".ijacocorc")

        result = su.bash.run(maven_command, check_returncode=0)

        time_used = time.time() - start
        return time_used, result

    # conduct experiment on one project by pass in the project name and coverage choice
    def exp_project(
        self,
        project: str,
        suffix: Optional[str] = "debug",
        coverage_choice: Optional[str] = "retestall",
        max_versions: Optional[int] = None,
        manual_version_list: Optional[List[str]] = None,
    ):
        logger.info(f"Experimenting on {project} using {coverage_choice} with suffix {suffix}.")

        # if the project not be cloned yet, clone the project to "_downloads" directory
        project_directory = self.work_dir / "_downloads" / project
        su.io.mkdir(project_directory.parent)
        # logger.info(project_directory)
        if not project_directory.exists():
            json_data = su.io.load(self.work_dir / "projects/projects.json")
            url = [item["url"] for item in json_data if item["name"] == project][0]
            su.bash.run(f"git clone {url} {project_directory}", check_returncode=0)

        version_list = su.io.load(self.work_dir / f"finerts-shas/{project}.json")

        if manual_version_list is not None:
            # run the manually specified versions for debugging
            version_list = manual_version_list
        elif max_versions is not None:
            # run the last "max_versions" versions, the version list is from newest to oldest
            version_list = version_list[:max_versions]

        data_directory = self.work_dir / f"results/{project}/{coverage_choice}_data"
        su.io.mkdir(data_directory)

        df = pd.DataFrame(columns=["Version", "#Files", "LOC", "#Class", "#Method", "Time"])
        with su.io.cd(project_directory):
            su.bash.run("git clean -fddx", check_returncode=0)

            # if JaCoCo is used as a default plugin, skip it when running experiments
            if check_jacoco_exists():
                logger.info(f"JaCoCo is a default build plugin for {project}, skip it.")

            for version in version_list:
                try:
                    # checkout the version
                    self.checkout_versions(version)

                    # # add profile to the POM
                    pom_add_profile(coverage_choice)

                    # check if the project needs special configuration on its pom
                    self.pom_config(project, version)

                    # read surefire reports data and coverage scores
                    df = self.surefire_data(df, project, coverage_choice, version, suffix)

                    # save the report logs to the data directory
                    save_reports(data_directory, project_directory, coverage_choice, version, suffix)

                except su.bash.BashError as e:
                    # log the error
                    logger.info(f"Error when building {project} with {coverage_choice}.")
                    su.io.dump(
                        self.work_dir / f"results/{project}/{coverage_choice}_data/{suffix}_error.log",
                        [f"Error on {project} with version {version} and coverage choice {coverage_choice}: \n{e}\n"],
                        fmt=su.io.fmts.txt_list,
                        append=True,
                    )
        su.bash.run(
            f"tar -czvf _work/results/{project}/{coverage_choice}_data/_log_{suffix}.tar.gz _work/results/{project}/"
            f"{coverage_choice}_data/_log_{suffix}",
            check_returncode=0,
        )
        su.bash.run(f"rm -r {data_directory}/_log_{suffix}", check_returncode=0)

    # run experiments for 5 times on a list of projects(projects.json) with selected coverage_choice,
    # retestall as default.
    def exp_projects(
        self,
        coverage_choice: Optional[str] = "retestall",
    ):
        num_exp = 5

        project_list_file = f"{self.work_dir}/projects/projects.json"

        for project in su.io.load(project_list_file):
            project_name, _url = project["name"], project["url"]
            all = True

            for suffix in range(num_exp):
                if coverage_choice == "ekstazi":
                    self.exp_project(project_name, suffix, "ekstazi")
                elif coverage_choice == "ijacoco":
                    self.exp_project(project_name, suffix, "ijacoco")
                elif coverage_choice == "bjacoco":
                    self.exp_project(project_name, suffix, "bjacoco")
                else:
                    self.exp_project(project_name, suffix)

                if not (self.work_dir / f"results/{project_name}/{coverage_choice}_data/_log_{suffix}.tar.gz").exists():
                    logger.info(f"{project_name}, {suffix}")
                    all = False

            # when all 5 runs finished, calculate the average
            if all:
                calculate_average(project_name, coverage_choice, num_exp)

    # check and log any test failures
    def check_test_failures(self, result: str, data_directory: str, project_name: str, version: str, suffix: str):
        # if there are any test failures when building the projects, document it to the log
        failure_tests = None

        error_strings = ["[ERROR] Failures:", "Failed tests:", "Crashed tests:", "Tests in error:"]
        index = -1  # Initialize index to -1 indicating no match found initially

        for error_string in error_strings:
            if error_string in result:
                index = result.find(error_string)
                failure_tests = result[index:]

        # if test failures exist, log it to data directory
        if failure_tests:
            log_test_failures = open(f"{data_directory}/{suffix}_test_failures.log", "a+")
            log_test_failures.write(f"Test failures on {project_name} with version {version}:\n {failure_tests}")
            logger.info(f"Test failures on {project_name} with version {version}\n")

    # read surefire reports folder, create csv file with coloumns: "Version", "#Files", "LOC", "#Class", '#Method',
    # "Time", for ijacoco and bjacoco, line/branch/instruction coverage scores are included
    def surefire_data(self, df: pd.DataFrame, project_name: str, coverage_choice: str, version: str, suffix: str):
        project_directory = self.work_dir / f"_downloads/{project_name}"

        data_directory = self.work_dir / f"results/{project_name}/{coverage_choice}_data"
        su.io.mkdir(data_directory)

        with su.io.cd(project_directory):
            # if ijacoco, delete the time logs from the previous version
            if coverage_choice == "ijacoco":
                su.bash.run("rm -rf .ekstazi/time-logs", check_returncode=0)

            # execution time
            time_used, result = self.run_maven_project(project_name, coverage_choice)
            logger.info(f"\n------------Success build on version {version} for {project_name}--------------\n")

            # dump execution outputs
            su.io.dump(project_directory / "target/surefire-reports/stdout.txt", result.stdout)
            su.io.dump(project_directory / "target/surefire-reports/stderr.txt", result.stderr)

            # number of java files
            num_files = re.match(r"\d+", su.bash.run("find . -name '*.java' | wc -l", check_returncode=0).stdout).group(
                0
            )

            loc = re.match(
                r"\d+", su.bash.run("cloc . | grep -E '^Java' | awk '{print $5}'", check_returncode=0).stdout
            ).group(0)

            # number of methods is the total number of testcase in each class
            num_method = 0
            # number of classes is the number of file under "surefire-reports" with >0 testcases
            num_class = 0

            surefire_dir = project_directory / "target/surefire-reports/"

            # detect number of test cases
            if not surefire_dir.exists():
                logger.info(f"Cannot find the surefire-reports folder on {project_name} for version {version}")
            else:
                for filename in os.listdir(surefire_dir):
                    if filename.endswith(".xml"):
                        filepath = surefire_dir / filename
                        with open(filepath, "r") as file:
                            count = sum(1 for line in file if line.strip().startswith("<testcase"))
                            # logger.info(f"{filename}: {count}")
                            num_method += count
                            if count > 0:
                                num_class += 1

            # add the data to a dictionary, and append to the dataframe
            row_dict = {
                "Version": version,
                "Profile Choice": coverage_choice,
                "#Files": num_files,
                "LOC": loc,
                "#Class": num_class,
                "#Method": num_method,
                "Time": time_used,
            }

            if coverage_choice in ["ijacoco", "bjacoco"]:
                logger.info(f"Reading {coverage_choice} coverage scores.")
                coverage_score = read_coverage(
                    f"{project_directory}/coverage-reports/{coverage_choice}-ut/{coverage_choice}.csv"
                )
                row_dict.update(coverage_score)
                # logger.info(row_dict)

            # if ijacoco, read the time logs
            if coverage_choice == "ijacoco":
                time_log = self._read_time_log(project_directory)
                row_dict.update({f"Time/{k}": v for k, v in time_log.items()})

            row = pd.DataFrame([row_dict])
            df = df._append(row)
            # save the dataframe to csv
            df.to_csv(data_directory / f"{suffix}_{coverage_choice}_data.csv", index=False)

            self.check_test_failures(result.stdout, data_directory, project_name, version, suffix)

        return df

    def _read_time_log(self, project_dir: Path) -> Dict[str, float]:
        """
        Read the time logs generated for each version.
        :param project_dir: The directory of the project.
        :return: A mapping from phase names to the time spent in seconds.
        """
        time_log_dir = project_dir / ".ekstazi" / "time-logs"
        event2ns = {}
        event2dur = collections.defaultdict(float)
        for f in time_log_dir.glob("*.log"):
            for line in su.io.load(f, su.io.fmts.txt_list):
                event, ns = line.rsplit("@", 1)
                event2ns[event] = int(ns)

                if event.endswith(":end"):
                    event_beg = event[:-4] + ":beg"
                    if event_beg in event2ns:
                        event2dur[event[:-4]] += (event2ns[event] - event2ns[event_beg]) / 1e9

        return {
            "analysis": event2dur.get("select", 0),
            "execution+collection": sum(duration for event, duration in event2dur.items() if event.startswith("test:")),
            "report": event2dur.get("report", 0),
        }


if __name__ == "__main__":
    su.log.setup()
    CLI(ProjectBuilder, as_positional=False)
