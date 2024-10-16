from pathlib import Path

import matplotlib.lines as mlines
import pandas as pd
import seaborn as sns
import seutil as su
from jsonargparse import CLI
from matplotlib import patches as patches
from matplotlib import pyplot as plt


class IndividualPlotGenerator:
    def __init__(self, paper_dir: su.arg.RPath = Path.cwd().parent / "ijacoco-paper", 
                 work_dir: su.arg.RPath = Path.cwd() / "_work"):  
        self.work_dir = work_dir
        self.paper_dir = paper_dir
        self.projects = ['apache_commons-codec', 'apache_commons-lang', 'apache_commons-net', 'alibaba_fastjson']
                        #  'finmath_finmath-lib', 'sonyxperiadev_gerrit-events'

    def make_plots(self):
        # key is plot name, in the list [0] is the y-axis, [1] is the y-axis label, [3] is the 
        plots_generation = {
            "execution_plot": ["Time", "Execution Time [s]"],
            "coverage_plot": ["Line Coverage", "Line Coverage [%]"],
            "speedup_plot": ["Speedup", "Speedup"],
            "test_selection_plot": ["Selected Test Rate", "Test Selection Rate [%]"]
            }
        for project_name in self.projects:
            for plot_name, info in plots_generation.items():
                y_axis, y_label = info[0], info[1]
                self.plot_generation(project_name, plot_name, y_axis, y_label)

    def plot_generation(self, project_name: str, plot_name:str, y_axis: str, y_label: str):
        # Execution Data Process
        ijacoco_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/ijacoco_data/average_data.csv")
        bjacoco_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/bjacoco_data/average_data.csv")
        ekstazi_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/ekstazi_data/average_data.csv")
        retestall_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/retestall_data/average_data.csv")

        ijacoco_avg_data["Version Index"] = range(1, 52)
        ijacoco_avg_data["Profile Choice"] = "ijacoco"
        ijacoco_avg_data["Selected Test Rate"] =  (ijacoco_avg_data["#Class"] / retestall_avg_data["#Class"]) 
        ijacoco_avg_data["Line Coverage"] = ijacoco_avg_data["Line Coverage"] 

        bjacoco_avg_data["Version Index"] = range(1, 52)
        bjacoco_avg_data["Profile Choice"] = "bjacoco"
        bjacoco_avg_data["Line Coverage"] = bjacoco_avg_data["Line Coverage"] 

        ekstazi_avg_data["Version Index"] = range(1, 52)
        ekstazi_avg_data["Profile Choice"] = "ekstazi"
        ekstazi_avg_data["Selected Test Rate"] = (ekstazi_avg_data["#Class"] / retestall_avg_data["#Class"]) 

        df = pd.concat([ijacoco_avg_data, bjacoco_avg_data, ekstazi_avg_data], axis=0)
        df["Speedup"] =  bjacoco_avg_data["Time"] / ijacoco_avg_data["Time"]

        plt.figure(figsize=(4, 3))
        if plot_name == "speedup_plot":
            sns.lineplot(data=df, x='Version Index', y=y_axis)
            plt.xlabel('Version')
            plt.ylabel(y_label)
            plt.axhline(y=1, color='#b3b3b3', linestyle='--')
            ax = plt.gca()
            ax.set_ylim(bottom=0)

        elif plot_name == "test_selection_plot":
            sns.lineplot(data=df[df['Profile Choice'] == 'ijacoco'],
                          x='Version Index', 
                          y=y_axis, 
                          label='iJaCoCo', 
                          linestyle='-')
            
            sns.lineplot(data=df[df['Profile Choice'] == 'ekstazi'], 
                         x='Version Index', 
                         y=y_axis, 
                         label='Ekstazi', 
                         linestyle='--')

             # Custom legend labels and colors
            labels = ["iJaCoCo", 'Ekstazi']
            colors = sns.color_palette().as_hex()[:len(labels)]
            handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
            plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(1, 0.94), ncol=2, numpoints=1)

           # Adding labels and title
            plt.xlabel('Version')
            plt.ylabel(y_label)
            ax = plt.gca()
            ax.set_ylim(0, 110)

        else:
            # Creating a line plot
            sns.lineplot(data=df[df['Profile Choice'] == 'ijacoco'], 
                         x='Version Index', 
                         y=y_axis, 
                         label='iJaCoCo', 
                         linestyle='-')
            
            sns.lineplot(data=df[df['Profile Choice'] == 'bjacoco'], 
                         x='Version Index', 
                         y=y_axis, 
                         label='bJaCoCo', 
                         linestyle='--')
            
            # Custom legend labels and colors
            labels = ["iJaCoCo", 'JaCoCo']
            colors = sns.color_palette().as_hex()[:len(labels)]
            handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
            plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(1, 0.94), ncol=2, numpoints=1)
            
            # Adding labels and title
            plt.xlabel('Version')
            plt.ylabel(y_label)

            ax = plt.gca()
            ax.set_ylim(bottom=0)
            if plot_name == "coverage_plot":
                ax.set_ylim(0, 110)
        
        plt.tight_layout()
        with su.io.cd(self.work_dir / "paper_data/plots"):
            plt.savefig(f"{project_name}_{plot_name}.png")
        with su.io.cd(self.paper_dir / "figs"):
            plt.savefig(f"{project_name}_{plot_name}.eps")

       # Clear the plot for the next project
        plt.clf()
        plt.close()

        return
    
if __name__ == "__main__":
    CLI(IndividualPlotGenerator, as_positional=False)