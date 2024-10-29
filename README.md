# iJaCoCo: Incremental Code Coverage Analysis Tool for Java

iJaCoCo is an incremental code coverage analysis tool for Java that builds on JaCoCo and Ekstazi, the state-of-the-art tools for code coverage analysis and regression test selection (RTS), respectively. Traditional code coverage tools like JaCoCo recompute coverage by executing all tests on each code change, which is time-consuming. iJaCoCo addresses this inefficiency by executing only a minimal subset of tests that are affected by code changes, reducing overhead and accelerating the analysis. Evaluated across 1,122 versions from 22 open-source repositories, iJaCoCo achieves speedups of 1.86× on average and up to 8.20× compared to JaCoCo, without sacrificing accuracy​. 

iJaCoCo is presented in the following ASE 2024 paper:

Title: [Efficient Incremental Code Coverage Analysis for Regression Test Suites](WangASE24iJaCoCo.pdf)

Authors: Jiale Amber Wang, Kaiyuan Wang, Pengyu Nie

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Citation](#citation)

## Prerequisites

- Linux operating system
- [Miniconda](https://docs.anaconda.com/miniconda/)
- [Java 8](https://www.oracle.com/java/technologies/javase/javase8-archive-downloads.html)
- [Maven 3.9](https://maven.apache.org/download.cgi)
- [cloc](https://github.com/AlDanial/cloc)

You can run `./check-prereq.sh` to check if you meet these prerequisites.

## Installation

Ensure the following commands can be found in PATH: `conda`, `mvn`. Then, you can install a conda environment for the experiment by running the following script:

```
./prepare-env.sh
```

After this script finishes, you can activate the conda environment by running:

```
conda activate ijacoco-research
```

## Usage

This section includes commands for running the experiments.
Unless otherwise specified, all commands should be run in the project root directory (`./` with respect to this README) and with the ijacoco-reseach conda environment activated.

To fairly compare the performance of iJaCoCo and JaCoCo, we forked the JaCoCo tool at the same version as the one iJaCoCo was built on, and renamed the tool name to bJaCoCo to avoid interference with existing JaCoCo configurations. 
The source code for iJaCoCo and bJaCoCo are in `./ijacoco` and `./bjacoco` respectively. They will be automatically installed during the first run. They can also be manually installed by running `mvn install` in each directory.


### Running all projects' all versions

#### RetestAll

This command will run all projects on all versions without any profile and output the data to `./_work/results/[project_name]/retestall_data`. The output result contains metrics including version, number of files, line of code, number of classes, number of methods, and execution time. The default number of experiments is 5.

```
python -m ijacoco.build_project --work_dir ./_work exp_projects
```

#### iJaCoCo

This command will run all projects on all versions with iJaCoCo and output the data to `./_work/results/[project_name]/ijacoco_data`. The output result contains metrics including version, number of files, line of code, number of classes, number of methods, execution time, and instruction/branch/line coverage. The default number of experiments is 5.

```
python -m ijacoco.build_project --work_dir ./_work exp_projects --coverage_choice ijacoco
```

#### bJaCoCo

This command will run all projects on all versions with bJaCoCo and output the data to `./_work/results/[project_name]/bjacoco_data`. The output result contains metrics including version, number of files, line of code, number of classes, number of methods,execution time and instruction/branch/line coverage. The default number of experiments is 5.

```
python -m ijacoco.build_project --work_dir ./_work exp_projects --coverage_choice bjacoco
```

#### Ekstazi

This command will run all projects on all versions with Ekstazi and output the data to `./_work/results/[project_name]/ekstazi_data`. The output result contains metrics including version, number of files, line of code, number of classes, number of methods, and execution time. The default number of experiments is 5.

```
python -m ijacoco.build_project --work_dir ./_work exp_projects --coverage_choice ekstazi
```

### Running one project's all versions under the selected configuration

Using project `apache_commons-collections` as an example, suffix is debug by default. The main function is `exp_project` in build_project.py. Experiment with the project under different configurations by changing the value of coverage_choice.

#### RetestAll:

```
python -m ijacoco.build_project --work_dir ./_work exp_project --project apache_commons-collections
```

#### bJaCoCo:

```
python -m ijacoco.build_project --work_dir ./_work exp_project --project apache_commons-collections --coverage_choice bjacoco
```

#### iJaCoCo:

```
python -m ijacoco.build_project --work_dir ./_work exp_project --project apache_commons-collections --coverage_choice ijacoco
```

#### Ekstazi:

```
python -m ijacoco.build_project --work_dir ./_work exp_project --project apache_commons-collections --coverage_choice ekstazi
```

## Dataset

Below is the structure of the dataset, relative to the work directory `./_work`:

- `results/$PROJ/`: results for project `$PROJ`
  - `$profile_data/`: results for the `$profile` in {`retestall`, `ijacoco`, `bjacoco`, `ekstazi`}
    - `$i_$profile_data.csv`: coverage summary results for the `$i`-th run
    - `average_data.csv`: average coverage summary results across multiple runs
    - `_log_$i.tar.gz`: execution logs for the `$i`-th run
  - `average_data.csv`: average coverage summary results combining all profiles and runs
  - `plot_$i.png`: coverage plots for the `$i`-th run
  - `plot_average.png`: coverage plots averaged across multiple runs
- `projects/`: list of projects used in the study
  - `projects.json`: list of projects
  - `projects_config.json`: special configurations for some of the projects
- `finerts-shas/`: list of versions used for each project, following those used by FineRTS


## Citation

```
@inproceedings{WangETAL24iJaCoCo,
  title =        {Efficient Incremental Code Coverage Analysis for Regression Test Suites},
  author =       {Jiale Amber Wang, Kaiyuan Wang, Pengyu Nie},
  booktitle =    {International Conference on Automated Software Engineering},
  year =         {2024},
}
```