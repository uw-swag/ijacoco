from pathlib import Path
import pandas as pd
import seutil as su
from jsonargparse import CLI
from ijacoco.paper.stat_test import sign_test_pairwise

class ProjectDataGenerator:

    def sign_diff_test(self):
        df = pd.DataFrame(columns=["Project Name", "Coverage p_neq","Coverage p_neq2","Coverage p_bjacoco_gt_ijacoco","Coverage p_ijacoco_gt_bjacoco", "Time p_neq","Time p_neq2","Time p_bjacoco_gt_ijacoco","Time p_ijacoco_gt_bjacoco"])
        for project in su.io.load('./_work/projects/projects.json'):
            project_name, _ = project["name"], project["url"]
            dict_ijacoco_bjacoco_coverage = {}
            dict_ijacoco_bjacoco_time = {}
            for choice in ["ijacoco", "bjacoco"]:
                coverage_data = []
                time_data = []
                for i in range(5):
                    data_file = Path(f'./_work/results/{project_name}/{choice}_data/{i}_{choice}_data.csv')
                    data = pd.read_csv(data_file)
                    coverage_data.extend(data["Line Coverage"].tolist())
                    time_data.extend(data["Time"].tolist())
                    dict_ijacoco_bjacoco_coverage[f"{project_name}_{choice}_coverage"] = coverage_data
                    dict_ijacoco_bjacoco_time[f"{project_name}_{choice}_time"] = time_data

            coverage_sign_test_result = sign_test_pairwise(dict_ijacoco_bjacoco_coverage)
            coverage_sign_test_result = {f"Coverage {k}": round(float(v), 3) for k, v in coverage_sign_test_result.items()}
            coverage_sign_test_result["Project Name"] = project_name
            df = df._append(coverage_sign_test_result, ignore_index=True)
            
            time_sign_test_result = sign_test_pairwise(dict_ijacoco_bjacoco_time, is_pairwise=True)
            time_sign_test_result = {k: round(float(v), 3) for k, v in time_sign_test_result.items()}
            for k, v in time_sign_test_result.items():
                df.loc[df.index[-1], f"Time {k}"] = v
        df.to_csv(f"_work/paper_data/sign_test_result.csv", index=False)
        coverage_check_data = pd.read_csv(f"./_work/paper_data/coverage_check.csv")
        coverage_check_data["No Stat Sign Diff"] = df["Coverage p_neq"] > 0.05
        coverage_check_data.to_csv("./_work/paper_data/coverage_check.csv", index=False)

        # Print projects with significant differences
        # significant_projects = df[(df['Coverage p_neq'] < 0.05) | (df['Time p_ijacoco_gt_bjacoco'] < 0.05)]
        # if not significant_projects.empty:
        #     print("Projects with significant differences (p < 0.05):")
        #     for _, row in significant_projects.iterrows():
        #         for metric in ['Coverage p_neq', 'Time p_ijacoco_gt_bjacoco']:
        #             if row[metric] < 0.05:
        #                 print(f"\nProject: {row['Project Name']}")
        #                 print(f"  {metric}: {row[metric]}")

    def retestall_ekstazi_avg_data(self):
        
        # calculate the aveerage value of "#Files", "LOC", "#Class", '#Method', "Time"
        def calculate_avg(choice):
            df = pd.DataFrame(columns=["Project Name", "#Files", "LOC", "#Class", '#Method', "Time"])
            for project in su.io.load('./_work/projects/projects.json'):
                project_name, _ = project["name"], project["url"]
                avg_data_file = Path(f'./_work/results/{project_name}/{choice}_data/average_data.csv')
                if not avg_data_file.exists():
                    continue
                avg_data = pd.read_csv(avg_data_file)
                # print(avg_data)
                metrics = ["#Files", "LOC", "#Class", '#Method', "Time"]
                avg_metrics = avg_data[metrics].mean().to_dict()  
                avg_metrics["Project Name"] = project_name  
                avg_metrics["Total Time"] = avg_data["Time"].sum()
                df = df._append(avg_metrics, ignore_index=True)  

            return df
        
        restestall_df = calculate_avg("retestall")
        ekstazi_df = calculate_avg("ekstazi")

        # calcluate selected test rate
        merged_df = pd.merge(ekstazi_df, restestall_df, on='Project Name', suffixes=('_ekstazi', '_restestall'))

        # Perform the division only when the "name" column has the same value
        ekstazi_df["Selected Test Rate"] = merged_df['#Class_ekstazi'] / merged_df['#Class_restestall'] 

        restestall_df.to_csv(f'_work/paper_data/retestall_avg_data.csv', index=False)
        ekstazi_df.to_csv(f'_work/paper_data/ekstazi_avg_data.csv', index=False)


    # this is a function to generate data for calculating overall arverage execution time, max/min/avg coverage for projects, and save data to paper_data/ijacoco_avg_data.csv and bjacoco_avg_data.csv
    def ibjacoco_avg_data(self):
        df = pd.DataFrame(columns=["Project Name", "Coverage Choice", "Time", "Min Time", "Max Time", "Total Time", "Instruction Coverage", "Branch Coverage", "Line Coverage", "Min Line Coverage", "Max Line Coverage", "#Files", "LOC", "#Class", '#Method'])
        for coverage_choice in ["ijacoco", 'bjacoco']:
            for project in su.io.load('./_work/projects/projects.json'):
                project_name, _ = project["name"], project["url"]
                avg_data_file = Path(f'./_work/results/{project_name}/{coverage_choice}_data/average_data.csv')
                if not avg_data_file.exists():
                    continue
                avg_data = pd.read_csv(avg_data_file)
                # print(avg_data)

                metrics = ["Time", "Instruction Coverage", "Line Coverage", "Branch Coverage", "#Files", "LOC", "#Class", '#Method']

                avg_df = avg_data[metrics].mean()
                avg_df["Min Time"] = avg_data['Time'].min()
                avg_df["Max Time"] = avg_data['Time'].max()
                avg_df["Total Time"] = avg_data['Time'].sum()
                avg_df["Min Line Coverage"] = avg_data['Line Coverage'].min()
                avg_df["Max Line Coverage"] = avg_data['Line Coverage'].max()
                avg_df["Project Name"] = project_name
                avg_df["Coverage Choice"] = coverage_choice
                df = df._append(avg_df, ignore_index=True)
            df.to_csv(f'_work/paper_data/{coverage_choice}_avg_data.csv', index=False)
            df = df.iloc[0:0]

        ijacoco_df = pd.read_csv(f"./_work/paper_data/ijacoco_avg_data.csv")
        bjacoco_df = pd.read_csv(f"./_work/paper_data/bjacoco_avg_data.csv")
        restestall_df = pd.read_csv("_work/paper_data/retestall_avg_data.csv")

        # Calculate Speedup
        ijacoco_df["Speedup"] = bjacoco_df["Time"] / ijacoco_df["Time"]

        # Calculate Selected Test Rate
        merged_df = pd.merge(ijacoco_df, restestall_df, on='Project Name', suffixes=('_ijacoco', '_restestall'))
        ijacoco_df["Selected Test Rate"] = (merged_df['#Class_ijacoco'] / merged_df['#Class_restestall'])*100

        ijacoco_df.to_csv(f'_work/paper_data/ijacoco_avg_data.csv', index=False)

    def projects_data(self):
        project_data_df = pd.DataFrame(columns=["Project Name", "URL", "Head", "#Ver", "#Files", "LOC", "#Class", '#Method', "Time"])
       
        ijacoco_internal_directory = Path.cwd()
        project_list_file = f"{ijacoco_internal_directory}/_work/projects/projects.json"

        for project in su.io.load(project_list_file):
            project_name, url = project["name"], project["url"]
            project_data_path = f"{ijacoco_internal_directory}/_work/results/{project_name}/retestall_data"
            average_data_file = f"{project_data_path}/average_data.csv"
            if Path(average_data_file).is_file():
                average_data_df = pd.read_csv(average_data_file)
                first_row = average_data_df.iloc[0]
                project_data_df = project_data_df._append({
                    "Project Name": project_name,
                    "URL": url,
                    "Head": first_row["Version"],
                    "#Ver": len(average_data_df),
                    "#Files": first_row["#Files"],
                    "LOC": first_row["LOC"],
                    "#Class": first_row["#Class"],
                    "#Method": first_row["#Method"],
                    "Time": first_row["Time"]
                }, ignore_index=True)
            else:
                project_data_df = project_data_df._append({
                    "Project Name": project_name,
                    "URL": url,
                    "Head": 0,
                    "#Ver": 0,
                    "#Files":0,
                    "LOC": 0,
                    "#Class": 0,
                    "#Method": 0,
                    "Time": 0}, ignore_index=True)

        project_data_df.to_csv('_work/paper_data/projects_data.csv', index=False)

    def phase_data(self):
            df = pd.DataFrame(columns=["Project", "Time/compile", "Time/analysis", "Time/execution+collection", "Time/report"])
            for project in su.io.load('./_work/projects/projects.json'):
                project_name, _ = project["name"], project["url"]
                # change file name
                avg_data_file = Path(f'./_work/results/{project_name}/ijacoco_data/0_ijacoco_data.csv')
                avg_data = pd.read_csv(avg_data_file)
                metrics = ["Time", "Time/analysis","Time/execution+collection","Time/report"]
                avg_metrics = avg_data[metrics].mean().to_dict()  
                avg_metrics["Project"] = project_name  
                avg_metrics["Time/compile"] = avg_metrics["Time"] - (avg_metrics["Time/analysis"] + avg_metrics["Time/execution+collection"] + avg_metrics["Time/report"])  

                # Calculate percentages
                total_time = avg_metrics["Time"]
                for phase in ["compile", "analysis", "execution+collection", "report"]:
                    phase_time = avg_metrics[f"Time/{phase}"]
                    avg_metrics[f"Percentage/{phase}"] = (phase_time / total_time) * 100
                
                df = df._append(avg_metrics, ignore_index=True)
        
                df.to_csv(f'_work/paper_data/phase_data.csv', index=False)

    # output coverage_check.csv
    def coverage_check_data(self):
        project_list_file = "_work/projects/projects.json"
        results = []

        # Load project list
        project_list = su.io.load(project_list_file)

        # Iterate over projects
        for project in project_list:
            project_name = project["name"]

            ###### calculate the std by get the averge of each run, then find the std of 5 runs
            # avg_list = []

            # # Read bjacoco files
            # for i in range(5):
            # 	bjacoco_file = f"_work/results/{project_name}/bjacoco_data/{i}_bjacoco_data.csv"
            # 	avergae_coverage = pd.read_csv(bjacoco_file)["Line Coverage"].mean()
            # 	avg_list.append(avergae_coverage)

            # # Concatenate bjacoco DataFrames
            # print(avg_list)
            # bjacoco_std = numpy.std(avg_list) 
            # bjacoco_mean = numpy.mean(avg_list)

            # print(bjacoco_std, bjacoco_mean)

            ###### calculate the std by averaging the std of 50 versions
            # list contains 5 elements, each is the Line Coverage data from suffix i
            bjacoco_cov_list = []
            ijacoco_cov_list = []

            # Loop through the 5 runs and read the CSV files
            for i in range(5):
                bjacoco_file = f"_work/results/{project_name}/bjacoco_data/{i}_bjacoco_data.csv"
                bjacoco_df = pd.read_csv(bjacoco_file)
                bjacoco_coverage = bjacoco_df[['Line Coverage']].add_suffix(f"_{i}")
                bjacoco_cov_list.append(bjacoco_coverage)
                

                ijacoco_file = f"_work/results/{project_name}/ijacoco_data/{i}_ijacoco_data.csv"
                ijacoco_df = pd.read_csv(ijacoco_file)
                ijacoco_coverage = ijacoco_df[['Line Coverage']].add_suffix(f"_{i}")
                ijacoco_cov_list.append(ijacoco_coverage)

            # the dataframe with size 50*5
            bjacoco_coverage_five_runs = pd.concat(bjacoco_cov_list, axis=1)
            # print(bjacoco_coverage_five_runs.head())

            # the std of each version over 5 runs
            std_each_version= bjacoco_coverage_five_runs.std(axis=1) 
            # the average of std in 50 versions
            bjacoco_std = std_each_version.mean()
            
            bjacoco_mean_each_version = bjacoco_coverage_five_runs.mean(axis=1) # mean of 5 runs
            bjacoco_mean = bjacoco_mean_each_version.mean()  # mean of 50 versions

            coverage_five_runs = pd.concat(ijacoco_cov_list, axis=1)
            ijacoco_mean_each_version = coverage_five_runs.mean(axis=1) # mean of 5 runs
            ijacoco_mean = ijacoco_mean_each_version.mean()  # mean of 50 versions

            # the dataframe contains the mean of each version, and calcuates the difference in mean
            diff_df = pd.DataFrame()
            diff_df["ijacoco_mean_each_version"] = ijacoco_mean_each_version
            diff_df["bjacoco_mean_each_version"] = bjacoco_mean_each_version

            # this is the difference of mean of each version
            diff_df["difference"] = abs(bjacoco_mean_each_version - ijacoco_mean_each_version)

            # the mean of all 50 versions
            mean_diff = diff_df["difference"].mean()

            results.append({
                "Project": project_name,
                "bJaCoCo STD": bjacoco_std,
                "iJaCoCo Coverage Mean": ijacoco_mean,
                "bJaCoCo Coverage Mean": bjacoco_mean,
                "|iJaCoCo Mean - bJaCoCo Mean|": mean_diff,
                "Exact Same": True if mean_diff < 0.1 else False,
                "Within STD": True if mean_diff < bjacoco_std else False,
                "Diff(STD - ABS)": bjacoco_std - abs(ijacoco_mean - bjacoco_mean)
            })
        
        results_df = pd.DataFrame(results) 

        results_df.to_csv("./_work/paper_data/coverage_check.csv", index=False)

    def all_avg_data(self):
        self.ibjacoco_avg_data()
        self.retestall_ekstazi_avg_data()
        self.projects_data()
        self.phase_data()
        self.coverage_check_data()
        self.sign_diff_test()

if __name__ == "__main__":
    CLI(ProjectDataGenerator, as_positional=False)