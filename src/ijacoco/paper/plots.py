import matplotlib.lines as mlines
import pandas as pd
import seaborn as sns
import seutil as su
from jsonargparse import CLI
from matplotlib import patches as patches
from matplotlib import pyplot as plt


class PlotsGenerator:
    def __init__(self, work_dir: su.arg.RPath, paper_dir: su.arg.RPath):
        self.work_dir = work_dir
        self.paper_dir = paper_dir

        # Extract the project names
        projects = [project["name"] for project in su.io.load(self.work_dir / "projects/projects.json")]
        projects_discard = ['jenkinsci_email-ext-plugin']

        for i in projects_discard:
            projects.remove(i)

        self.projects = projects

    def make_plots(self):
        self.execution_speedup_data("bjacoco", "ijacoco" )
        self.execution_speedup_data("retestall", "ekstazi" )

        # generate the speedup plots
        self.make_plot_speedup("speedup_bjacoco_ijacoco")
        self.make_plot_speedup("speedup_retestall_ekstazi")

        # compare ekstazi speedup on retestall with ijacoco speedup on bjacoco 
        self.make_plot_speedup_compare() 

        self.execution_time_data()
        self.make_plot_execution_time()
        
        self.selection_rate_data()
        self.make_plot_selection_rate()   

        self.coverage_data()
        self.make_plot_coverage() 

    # generates ekstazi and ijacoco test selection rate dataframe, and save as csv file
    def selection_rate_data(self):
        all_data = []

        for project_name in  self.projects:
            data_files = {
                'retestall': self.work_dir / f"results/{project_name}/retestall_data/average_data.csv",
                'ekstazi': self.work_dir / f"results/{project_name}/ekstazi_data/average_data.csv",
                'ijacoco':  self.work_dir / f"results/{project_name}/ijacoco_data/average_data.csv"
            }
            
            try:
                retestall_avg_data = pd.read_csv(data_files['retestall'])
                retestall_selected_tests = retestall_avg_data["#Class"]
                ekstazi_avg_data = pd.read_csv(data_files['ekstazi'])
                ijacoco_avg_data = pd.read_csv(data_files['ijacoco'])
            except FileNotFoundError:
                continue

            ekstazi_project_data = pd.DataFrame({
                "Project": project_name,
                "Version": ekstazi_avg_data["Version"],
                "Version Index" : range(1, 52), # add version index coloumn for x-axis in plot
                "#Class": ekstazi_avg_data["#Class"],
                "Coverage Choice": "ekstazi",
                "Selected Test Rate": ekstazi_avg_data["#Class"] / retestall_selected_tests
                })
            
            ijacoco_project_data = pd.DataFrame({
                "Project": project_name,
                "Version": ijacoco_avg_data["Version"],
                "Version Index" : range(1, 52), # add version index coloumn for x-axis in plot
                "#Class": ijacoco_avg_data["#Class"],
                "Coverage Choice": "ijacoco",
                "Selected Test Rate": ijacoco_avg_data["#Class"] / retestall_selected_tests
                })
            
            # add ekstazi and ijacoco data to "all_data" dataframe
            all_data.append(ekstazi_project_data)
            all_data.append(ijacoco_project_data)

        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv( self.work_dir / "paper_data/selection_rate_data.csv", index=False)
            return df
        else:
            print("No data found to process.")
            return 
        

    def coverage_data(self):
        all_data = []

        for project_name in  self.projects:
            
            try:
                ijacoco_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/ijacoco_data/average_data.csv")
                bjacoco_avg_data = pd.read_csv(self.work_dir / f"results/{project_name}/bjacoco_data/average_data.csv")
            except FileNotFoundError:
                continue

            ijacoco_project_data = pd.DataFrame({
                "Project": project_name,
                "Version": ijacoco_avg_data["Version"],
                "Version Index" : range(1, 52), # add version index coloumn for x-axis in plot
                "Coverage Choice": "ijacoco",
                "Line Coverage": ijacoco_avg_data["Line Coverage"]
                })
            
            bjacoco_project_data = pd.DataFrame({
            "Project": project_name,
                "Version": ijacoco_avg_data["Version"],
                "Version Index" : range(1, 52), # add version index coloumn for x-axis in plot
                "Coverage Choice": "bjacoco",
                "Line Coverage": bjacoco_avg_data["Line Coverage"]
            })
              
            
            # add ijacoco and bjacooc data to "all_data" dataframe
            all_data.append(ijacoco_project_data)
            all_data.append(bjacoco_project_data)

        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv( self.work_dir / "paper_data/coverage_data.csv", index=False)
            return df
        else:
            print("No data found to process.")
            return 

    # generates the ijacoco and bjacoco execution time dataframe, and save as csv file
    def execution_speedup_data(self, data_1: str, data_2: str):
        all_data = []
        
        for project_name in self.projects:
            data_files = {
                # data_1: bjacoco  # data_2: ijacoco
                data_1: self.work_dir / f"results/{project_name}/{data_1}_data/average_data.csv",
                data_2: self.work_dir / f"results/{project_name}/{data_2}_data/average_data.csv"
            }
            
            try:
                data_1_avg_data = pd.read_csv(data_files[data_1])
                data_2_avg_data = pd.read_csv(data_files[data_2])
            except FileNotFoundError:
                continue

            speedup_data = pd.DataFrame({
                "Project": project_name,
                "Version": data_1_avg_data["Version"],
                "Version Index" : range(1, 52),
                "Speedup": data_1_avg_data["Time"] / data_2_avg_data["Time"]
                })
        
            # add ijacoco and bjacoco data to "all_data"
            all_data.append(speedup_data)
        
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv(self.work_dir / f"paper_data/speedup_{data_1}_{data_2}.csv", index=False)
            return df
        else:
            print("No data found to process.")
            return 

    def execution_time_data(self):
        all_data = []

        for project_name in self.projects:
            data_files = {
                'bjacoco': self.work_dir / f"results/{project_name}/bjacoco_data/average_data.csv",
                'ijacoco': self.work_dir / f"results/{project_name}/ijacoco_data/average_data.csv"
            }

            try:
                bjacoco_avg_data = pd.read_csv(data_files['bjacoco'])
                ijacoco_avg_data = pd.read_csv(data_files['ijacoco'])
            except FileNotFoundError:
                continue

            bjacoco_project_data = pd.DataFrame({
                "Project": project_name,
                "Version": bjacoco_avg_data["Version"],
                "Version Index" : range(1, 52),
                "Time": bjacoco_avg_data["Time"],
                "Coverage Choice": "bjacoco"
                })

            ijacoco_project_data = pd.DataFrame({
                "Project": project_name,
                "Version": bjacoco_avg_data["Version"],
                "Version Index" : range(1, 52),
                "Time": ijacoco_avg_data["Time"].astype(float),
                "Coverage Choice": "ijacoco"
                })

            # add ijacoco and bjacoco data to "all_data"
            all_data.append(bjacoco_project_data)
            all_data.append(ijacoco_project_data)

        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df.to_csv(self.work_dir / "paper_data/execution_time_data.csv", index=False)
            return df
        else:
            print("No data found to process.")
            return 

    def make_plot_execution_time(self):
        # load data
        df = pd.read_csv(self.work_dir / "paper_data/execution_time_data.csv")

        hue_order = ["ijacoco", "bjacoco"]
        dashes = [[], [1,1]]
        
        # get the sorted project names for ordering plots
        project_names_sorted = sorted(self.projects, key=lambda x: x.split("_")[1].lower())

        grid: sns.FacetGrid = sns.FacetGrid(
            df,
            col = "Project",
            col_order = project_names_sorted,
            col_wrap=4,
            hue = "Coverage Choice",
            hue_order=hue_order, 
            hue_kws=dict(dashes=dashes),
            sharex=False,
            sharey=False,
            height=2.5, aspect=1.3
        )

        grid = (grid.map_dataframe(sns.lineplot,x="Version Index", y="Time" ))
        for ax, title in zip(grid.axes.flat, grid.col_names):
            col_name = title.split("_")[1] 
            ax.set_title(col_name)
            ax.set_ylim(bottom=0)

        # add legend 
        labels = ["iJaCoCo", 'JaCoCo']
        colors = sns.color_palette().as_hex()[:len(labels)]
        handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab,)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
        plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(2.03, 0.25), ncol=1, numpoints=1)
        
        grid.set_xlabels("Version")
        grid.set_ylabels("Execution Time [s]")

        with su.io.cd(self.work_dir / "paper_data/plots"):
            grid.savefig("execution_time_plot.png")
        with su.io.cd(self.paper_dir / "figs"):
            grid.savefig("execution_time_plot.eps")
        return
    
    def make_plot_coverage(self):
        # load data
        df = pd.read_csv(self.work_dir / "paper_data/coverage_data.csv")
        df["Line Coverage"]  = df["Line Coverage"] 

        hue_order = ["ijacoco", "bjacoco"]
        dashes = [[], [1,1]]
        
        # get the sorted project names for ordering plots
        project_names_sorted = sorted(self.projects, key=lambda x: x.split("_")[1].lower())

        grid: sns.FacetGrid = sns.FacetGrid(
            df,
            col = "Project",
            col_order = project_names_sorted,
            col_wrap=4,
            hue = "Coverage Choice",
            hue_order=hue_order, 
            hue_kws=dict(dashes=dashes),
            sharex=False,
            height=2.5, aspect=1.3
        )

        grid = (grid.map_dataframe(sns.lineplot,x="Version Index", y="Line Coverage" )
            .set(
                ylim=(0, 110),
            ))
        for ax, title in zip(grid.axes.flat, grid.col_names):
            col_name = title.split("_")[1] 
            ax.set_title(col_name)

        # add legend 
        labels = ["iJaCoCo", 'JaCoCo']
        colors = sns.color_palette().as_hex()[:len(labels)]
        handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab,)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
        plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(2.03, 0.25), ncol=1, numpoints=1)
        
        grid.set_xlabels("Version")
        grid.set_ylabels("Line Coverage [%]")

        with su.io.cd(self.work_dir / "paper_data/plots"):
            grid.savefig("coverage_plot.png")
        with su.io.cd(self.paper_dir / "figs"):
            grid.savefig("coverage_plot.eps")
        return
    

    def make_plot_speedup(self, data_file_name: str):
        # load data
        df = pd.read_csv(self.work_dir / f"paper_data/{data_file_name}.csv")

        # get the sorted project names for ordering plots
        project_names_sorted = sorted(self.projects, key=lambda x: x.split("_")[1].lower())

        grid: sns.FacetGrid = sns.FacetGrid(
            df,
            col = "Project",
            col_order = project_names_sorted,
            col_wrap=4,
            sharex=False,        
            sharey=False,
            height=2.5, aspect=1.3
        )

        grid = (grid.map_dataframe(sns.lineplot,x="Version Index", y="Speedup" ))
        for ax, title in zip(grid.axes.flat, grid.col_names):
            col_name = title.split("_")[1]  
            ax.set_title(col_name)
            ax.set_ylim(bottom=0)
            ax.axhline(y=1, color='#b3b3b3', linestyle='--')
        
        grid.set_xlabels("Version")
        grid.set_ylabels("Speedup")

        with su.io.cd(self.work_dir / "paper_data/plots"):
            grid.savefig(f"{data_file_name}_plot.png")
        with su.io.cd(self.paper_dir / "figs"):
            grid.savefig(f"{data_file_name}_plot.eps")
        return

    def make_plot_selection_rate(self):
        df = pd.read_csv(self.work_dir / "paper_data/selection_rate_data.csv")
        df["Selected Test Rate"]  = df["Selected Test Rate"] 
        hue_order = ["ijacoco", "ekstazi"]
        dashes = [[], [1,1]]

        # get the sorted project names for ordering plots
        project_names_sorted = sorted(self.projects, key=lambda x: x.split("_")[1].lower())

        grid: sns.FacetGrid = sns.FacetGrid(
            df,
            col = "Project",
            col_order = project_names_sorted,
            col_wrap=4,
            hue = "Coverage Choice",
            hue_order=hue_order, 
            hue_kws=dict(dashes=dashes),
            sharex=False,
            height=2.5, aspect=1.3
        )

        grid = (grid.map_dataframe(sns.lineplot,x="Version Index", y="Selected Test Rate" )
            .set(
                ylim=(0, 110),
            ))
        
        for ax, title in zip(grid.axes.flat, grid.col_names):
            col_name = title.split("_")[1]  
            ax.set_title(col_name)
        
        # add legend 
        labels = ["iJaCoCo", "Ekstazi"] 
        colors = sns.color_palette().as_hex()[:len(labels)]
        handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab,)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
        plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(1.8, 0.25), ncol=1, numpoints=1)
        
        grid.set_xlabels("Version")
        grid.set_ylabels("Test Selection Rate [%]")

        with su.io.cd(self.work_dir / "paper_data/plots"):
            grid.savefig("selection_rate_plot.png")
        with su.io.cd(self.paper_dir / "figs"):
            grid.savefig("selection_rate_plot.eps")
        return


    def make_plot_speedup_compare(self):
        df_1 = pd.read_csv(self.work_dir / "paper_data/speedup_bjacoco_ijacoco.csv")
        df_2 = pd.read_csv(self.work_dir / "paper_data/speedup_retestall_ekstazi.csv")
        df_1["config"] = "iJaCoCo-JaCoCo"
        df_2["config"] = "Ekstazi-RetestAll"
        speedup_df = df_1._append(df_2)
        hue_order = speedup_df['config'].unique() 
        dashes = [[], [1,1]]

        # get the sorted project names for ordering plots
        project_names_sorted = sorted(self.projects, key=lambda x: x.split("_")[1].lower())

        grid: sns.FacetGrid = sns.FacetGrid(
            speedup_df,
            col = "Project",
            col_order = project_names_sorted,
            col_wrap=4,
            hue = "config",
            hue_order=hue_order, 
            hue_kws=dict(dashes=dashes),
            sharex=False,
            sharey=False,
            height=2.5, aspect=1.3
        )

        grid = (grid.map_dataframe(sns.lineplot,x="Version Index", y="Speedup"))
        
        for ax, title in zip(grid.axes.flat, grid.col_names):
            col_name = title.split("_")[1]
            ax.set_title(col_name)
            ax.set_ylim(bottom=0)
            ax.axhline(y=1, color='#b3b3b3', linestyle='--')

        # add legend 
        labels = hue_order 
        colors = sns.color_palette().as_hex()[:len(labels)]
        handles = [
                mlines.Line2D([], [], color=col, linestyle=ls, label=lab,)
                for col, ls, lab in zip(colors, ['-', '--'], labels)
            ]
        plt.legend(handles=handles, title="", loc="lower right", bbox_to_anchor=(2.04, 0.25), ncol=1, numpoints=1)
        
        grid.set_xlabels("Version")
        grid.set_ylabels("Speedup")

        with su.io.cd(self.work_dir / "paper_data/plots"):
            grid.savefig("speedup_compare_plot.png")
        with su.io.cd(self.paper_dir / "figs"):
            grid.savefig("speedup_compare_plot.eps")
        return
if __name__ == "__main__":
    CLI(PlotsGenerator, as_positional=False)