from pathlib import Path

import seutil as su
from jsonargparse import CLI

from ijacoco.paper.numbers_helper import (
    add_coverage_data,
    add_ibjacoco_data,
    add_projects_data,
    add_retestall_ekstazi_data,
    add_phase_data
)


class ResultsPaperGenerator:

    def __init__(self, paper_dir: su.arg.RPath = Path.cwd().parent / "ijacoco-paper", work_dir: su.arg.RPath = Path.cwd() / "_work"):
        self.paper_dir = paper_dir
        self.work_dir = work_dir

        projects = [project["name"] for project in su.io.load(self.work_dir / "projects/projects.json")]

        self.projects = projects

    def all_tables(self):
        self.numbers_results()
        self.table_projects_results()
        self.table_results()
        self.table_results_performance()
        self.table_results_coverage()
        self.table_results_selected_test_and_phase_time()

    def numbers_results(self):
        f = su.latex.File(self.paper_dir / "tables" / "numbers-results.tex")
        total_f = su.latex.File(self.paper_dir / "tables" /"numbers-sum-and-avg.tex")

        add_retestall_ekstazi_data("retestall", self.work_dir, f, total_f, self.projects)
        add_retestall_ekstazi_data("ekstazi", self.work_dir, f, total_f, self.projects)
        add_ibjacoco_data(self.work_dir, f, total_f, self.projects)
        add_projects_data(self.work_dir, f, total_f, self.projects)
        add_coverage_data(self.work_dir, f)
        add_phase_data(self.work_dir, f)

    def table_results(self): 
        f = su.latex.File(self.paper_dir / "tables" / "table-results.tex")

        f.append("\\begin{tabular}{lrrr}\\toprule Project & $T_i$ & $T_b$ & $T_b / T_i$ \\\\ \\midrule")

        project_name = self.projects
        project_name_sorted = sorted(project_name, key=lambda x: x.split("_")[1].lower())
    
        for name in project_name_sorted:
            name = name.replace("_", "-")
            f.append(f"\\UseMacro{{res-{name}-name}} & \\UseMacro{{res-{name}-ijacoco-time}} & \\UseMacro{{res-{name}-bjacoco-time}} & \\UseMacro{{res-{name}-ibjacoco-speedup-time}}\\\\")

        f.append("\\bottomrule\\end{tabular}")
        f.save()

    def table_projects_results(self): 
        f = su.latex.File(self.paper_dir / "tables" / "table-projects.tex")

        f.append(r"\begin{tabular}{l|l|c|r|r|r|r|r}")
    
        f.append(r"\toprule")

        f.append(r"\multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\UseMacro{TH-project}}}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\UseMacro{TH-head-revision}}}} & \multicolumn{1}{c|}{\multirow{2}{*}{\textbf{\UseMacro{TH-num-revision}}}} & \multicolumn{2}{c|}{\textbf{\UseMacro{TH-project-size}}} & \multicolumn{3}{c}{\textbf{\UseMacro{TH-project-test}}} \\")
        
        f.append(r"& & & \multicolumn{1}{c}{\UseMacro{TH-num-file}} & \multicolumn{1}{c|}{\UseMacro{TH-loc}} & \multicolumn{1}{c}{\UseMacro{TH-num-test-class}} & \multicolumn{1}{c}{\UseMacro{TH-num-test-method}} & \multicolumn{1}{c}{\UseMacro{TH-test-time}} \\")
         
        f.append(r"\midrule")

        project_name = self.projects
        project_name_sorted = sorted(project_name, key=lambda x: x.split("_")[1].lower())
    
        for name in project_name_sorted:
            name = name.replace("_", "-")

            f.append(f"\\href{{\\UseMacro{{res-{name}-url}}}}{{\\UseMacro{{res-{name}-name}}}} & \\texttt{{\\UseMacro{{res-{name}-head}}}} & \\UseMacro{{res-{name}-num-ver}} & \\UseMacro{{res-{name}-num-file}} & \\UseMacro{{res-{name}-loc}} & \\UseMacro{{res-{name}-num-class}} & \\UseMacro{{res-{name}-num-method}} & \\UseMacro{{res-{name}-time}}    \\\\")
        
        f.append("\\midrule")
        f.append("\\multicolumn{1}{c|}{\\UseMacro{TH-sum}} & \\UseMacro{TH-na} & \\UseMacro{TH-na} & \\UseMacro{res-projects-sum-num-file} & \\UseMacro{res-projects-sum-loc} & \\UseMacro{res-projects-sum-num-test-class} & \\UseMacro{res-projects-sum-num-test-method} & \\UseMacro{res-projects-sum-time} \\\\")
        f.append("\\bottomrule \\end{tabular}")
        f.save()


    def table_results_coverage(self):
        f = su.latex.File(self.paper_dir / "tables" / "table-results-coverage.tex")

        f.append(r"\begin{tabular}{l |r|r|r |r|r|r |r |r|r}")
        f.append(r"\toprule")
        f.append(r"\multicolumn{1}{c|}{\multirow{3}{*}{\textbf{\UseMacro{TH-project}}}} & \multicolumn{7}{c|}{\textbf{\UseMacro{TH-coverage}}} & \multicolumn{2}{c}{\textbf{\UseMacro{TH-correctness}}} \\")
        f.append( r"& \multicolumn{3}{c|}{\bjacoco} & \multicolumn{3}{c|}{\ijacocoTool} &  & \multirow{2}{*}{\UseMacro{TH-exact-same}} & \multirow{2}{*}{\UseMacro{TH-no-stat-sign-diff}}\\")
        f.append( r"& \UseMacro{TH-min} & \UseMacro{TH-max} & \UseMacro{TH-avg} & \UseMacro{TH-min} & \UseMacro{TH-max} & \UseMacro{TH-avg} & \multicolumn{1}{c|}{\UseMacro{TH-diff}} &  &\\")
        f.append(r"\midrule")

        project_name = self.projects
        project_name_sorted = sorted(project_name, key=lambda x: x.split("_")[1].lower())
        # print(project_name_sorted)

        for name in project_name_sorted:
            name = name.replace("_", "-")
            
            f.append(f"\\UseMacro{{res-{name}-name}} & \\UseMacro{{res-{name}-bjacoco-min-coverage}} & \\UseMacro{{res-{name}-bjacoco-max-coverage}} & \\UseMacro{{res-{name}-bjacoco-coverage}} & \\UseMacro{{res-{name}-ijacoco-min-coverage}} & \\UseMacro{{res-{name}-ijacoco-max-coverage}} & \\UseMacro{{res-{name}-ijacoco-coverage}} &  \\UseMacro{{{name}-coverage-diff}} & \\UseMacro{{{name}-coverage-exact-same}} & \\UseMacro{{{name}-coverage-no-stat-sign-diff}} \\\\")

        f.append("\\bottomrule \\end{tabular}")
        f.save()        

    def table_results_selected_test_and_phase_time(self):
        f = su.latex.File(self.paper_dir / "tables" / "table-results-selected-test-and-phase-time.tex")
        f.append(r"\begin{tabular}{l|r|r|r|r|r|r}")
        f.append(r"\toprule")
        f.append(r"\multicolumn{1}{c|}{\multirow{3}{*}{\textbf{\UseMacro{TH-project}}}} & \multicolumn{2}{c|}{\textbf{\UseMacro{TH-selected-test-ratio}}} & \multicolumn{4}{c}{\textbf{\UseMacro{TH-phase-time}}} \\")
        f.append(r" & \multicolumn{1}{c|}{\ekstazi} & \multicolumn{1}{c|}{\ijacocoTool} & \multicolumn{1}{c|}{\UseMacro{TH-compile-time}} & \multicolumn{1}{c|}{\UseMacro{TH-analysis-time}} & \multicolumn{1}{c|}{\UseMacro{TH-execution-collection-time}} & \multicolumn{1}{c}{\UseMacro{TH-report-time}} \\ ")
        f.append(r"\midrule")

        project_name = self.projects
        project_name_sorted = sorted(project_name, key=lambda x: x.split("_")[1].lower())

        for name in project_name_sorted:
            name = name.replace("_", "-")
            f.append(f"\\UseMacro{{res-{name}-name}} & "
                     f"\\UseMacro{{res-{name}-ekstazi-selected-rate}} & "
                     f"\\UseMacro{{res-{name}-ijacoco-selected-rate}} & "
                     f"\\UseMacro{{res-{name}-phase-compile}} (\\UseMacro{{res-{name}-phase-compile-percent}}\\%) & "
                     f"\\UseMacro{{res-{name}-phase-analysis}} (\\UseMacro{{res-{name}-phase-analysis-percent}}\\%) & "
                     f"\\UseMacro{{res-{name}-phase-execution-collection}} (\\UseMacro{{res-{name}-phase-execution-collection-percent}}\\%) & "
                     f"\\UseMacro{{res-{name}-phase-report}} (\\UseMacro{{res-{name}-phase-report-percent}}\\%)\\\\")

        f.append(r"\midrule")
        f.append(r"\multicolumn{1}{c|}{\textbf{\UseMacro{TH-avg}}} & "
                 r"\UseMacro{res-ekstazi-selected-test-rate-mean} & "
                 r"\UseMacro{res-ijacoco-selected-test-rate-mean} & "
                 r"\UseMacro{res-phase-avg-compile} (\UseMacro{res-phase-avg-compile-percent}\%) & "
                 r"\UseMacro{res-phase-avg-analysis} (\UseMacro{res-phase-avg-analysis-percent}\%) & "
                 r"\UseMacro{res-phase-avg-execution-collection} (\UseMacro{res-phase-avg-execution-collection-percent}\%) & "
                 r"\UseMacro{res-phase-avg-report} (\UseMacro{res-phase-avg-report-percent}\%) \\ ")
        
        f.append("\\bottomrule\\end{tabular}")
        f.save()


    def table_results_performance(self):
        f = su.latex.File(self.paper_dir / "tables" / "table-results-performance.tex")

        f.append(r"\begin{tabular}{l| r|r| r|r| r|r| r|r| r}")
        f.append(r"\toprule")
        f.append(r"\multicolumn{1}{c|}{\multirow{3}{*}{\textbf{\UseMacro{TH-project}}}} & \multicolumn{8}{c|}{\textbf{\UseMacro{TH-test-time}}} & \multicolumn{1}{c}{\textbf{\UseMacro{TH-speedup}}} \\")
     
        f.append( r"& \multicolumn{2}{c|}{\retestall} & \multicolumn{2}{c|}{\ekstazi} & \multicolumn{2}{c|}{\bjacoco} & \multicolumn{2}{c|}{\ijacocoTool} & \ijacocoTool \\")
        
        f.append( r"& \multicolumn{1}{c|}{\UseMacro{TH-avg}} & \multicolumn{1}{c|}{\UseMacro{TH-sum}} & \multicolumn{1}{c|}{\UseMacro{TH-avg}} & \multicolumn{1}{c|}{\UseMacro{TH-sum}} & \multicolumn{1}{c|}{\UseMacro{TH-avg}} & \multicolumn{1}{c|}{\UseMacro{TH-sum}} & \multicolumn{1}{c|}{\UseMacro{TH-avg}} & \multicolumn{1}{c|}{\UseMacro{TH-sum}} & \multicolumn{1}{c}{\UseMacro{TH-avg}}\\")
 
        f.append(r"\midrule")

        project_name = self.projects
        project_name_sorted = sorted(project_name, key=lambda x: x.split("_")[1].lower())
    
        for name in project_name_sorted:
            name = name.replace("_", "-")
            
            f.append(f"\\UseMacro{{res-{name}-name}} & \\UseMacro{{res-{name}-retestall-time}} & \\UseMacro{{res-{name}-retestall-total-time}} & \\UseMacro{{res-{name}-ekstazi-time}} & \\UseMacro{{res-{name}-ekstazi-total-time}} & \\UseMacro{{res-{name}-bjacoco-time}} & \\UseMacro{{res-{name}-total-bjacoco-time}}  & \\UseMacro{{res-{name}-ijacoco-time}} & \\UseMacro{{res-{name}-total-ijacoco-time}} & \\UseMacro{{res-{name}-ibjacoco-speedup-time}} \\\\")

        f.append(r"\midrule")
        f.append(r"\multicolumn{1}{c|}{\textbf{\UseMacro{TH-avg}}} &  \UseMacro{retestall-avg-time} & \UseMacro{retestall-avg-total-time} & \UseMacro{ekstazi-avg-time} & \UseMacro{ekstazi-avg-total-time} & \UseMacro{bjacoco-avg-time} & \UseMacro{bjacoco-avg-total-time}  & \UseMacro{ijacoco-avg-time} & \UseMacro{ijacoco-avg-total-time} & \UseMacro{ijacoco-avg-speedup} \\ ")

        # f.append(r"\multicolumn{1}{c|}{\textbf{\UseMacro{TH-sum}}} & \UseMacro{retestall-sum-time} & \UseMacro{retestall-sum-total-time} & \UseMacro{ekstazi-sum-time} & \UseMacro{ekstazi-sum-total-time} & \UseMacro{bjacoco-sum-time} & \UseMacro{bjacoco-sum-total-time}  & \UseMacro{ijacoco-sum-time} & \UseMacro{ijacoco-sum-total-time} & \UseMacro{TH-na}  \\ ")

        f.append("\\bottomrule \\end{tabular}")
        f.save()        

if __name__ == "__main__":
    CLI(ResultsPaperGenerator, as_positional=False)