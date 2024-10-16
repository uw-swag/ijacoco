from pathlib import Path
import sys

import pandas as pd
import seutil as su
import numpy

# compare rts paper ekstazi selection rate with our results
def rts_ekstazi_selection_rate_verify():
	finerts_data = pd.read_csv("./_work/paper_data/finerts_selection_rate.csv")
	current_data = pd.read_csv("./_work/paper_data/ekstazi_avg_data.csv")
	merged_df = pd.merge(finerts_data, current_data, on="Project Name")
	df = merged_df[["Project Name", "Selection Rate RTS"]]
	df["Selection Rate"] = (merged_df["Selected Test Rate"]*100).round(2)
	df["Difference"] = df["Selection Rate"] - df["Selection Rate RTS"]
	print(df)
	print("The mean in difference is ", df["Difference"].mean())
	print("The max in difference is ", df["Difference"].max())
	print("The min in difference is ", df["Difference"].min())
	df.to_csv("./_work/paper_data/selection_rate_ekstazi_verify.csv")
# rts_ekstazi_selection_rate_verify()


def fork_diff():
	csv_files = [] 
	first_rows = []
	project_list_file = "_work/projects/projects.json"

	for project in su.io.load(project_list_file):
		project_name = project["name"]
		csv_file_path = f"_work/results/{project_name}/bjacoco_data/average_data.csv"
		csv_files.append(csv_file_path)
		
		df = pd.read_csv(csv_file_path)
		
		if not df.empty:
			first_row = df.iloc[0]  # Extract the first row
			first_row["Project"] = project_name  # Add project name to the first row
			first_rows.append(first_row)

	bjacoco_df = pd.DataFrame(first_rows).reset_index(drop=True)
	bjacoco_df.to_csv("./_work/paper_data/bjacoco_first_version.csv", index=False)

	bjacoco_fork_df = pd.read_csv("./_work/paper_data/bjacoco_forked.csv")  

	diff_df = pd.DataFrame()
	diff_df["Project"] = bjacoco_fork_df["Project"]
	diff_df["Time_bjacoco_forked"] = bjacoco_fork_df["Time"]
	diff_df["Time_bjacoco"] = pd.to_numeric(bjacoco_df["Time"], errors='coerce')
	diff_df['Difference'] = (diff_df["Time_bjacoco_forked"] - diff_df["Time_bjacoco"]) / diff_df["Time_bjacoco"]
	diff_df.to_csv("./_work/paper_data/bjacoco_fork_diff.csv", index=False)

	print(diff_df)
	print(diff_df["Difference"].mean())

# fork_diff()