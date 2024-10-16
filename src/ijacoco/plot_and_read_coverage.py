import matplotlib.pyplot as plt
import pandas as pd
import seutil as su

# reads the coverage result from the raw csv data file in project directory(coverage-reports)
def read_coverage(csv_file):
	metrics_columns = ['INSTRUCTION', 'BRANCH', 'LINE']
	dic = {"Instruction Coverage": 0, "Branch Coverage":0, "Line Coverage": 0}
	try:
		df = pd.read_csv(csv_file)
		for metric in metrics_columns:
			covered_column = df[f'{metric}_COVERED'].sum()
			missed_column = df[f'{metric}_MISSED'].sum()
			coverage = covered_column / (covered_column + missed_column)
			if metric == "INSTRUCTION":
				dic["Instruction Coverage"] = coverage * 100
			if metric == "BRANCH":
				dic["Branch Coverage"] = coverage * 100 
			if metric == "LINE":
				dic["Line Coverage"] = coverage * 100
	except pd.errors.EmptyDataError:
		print("The coverage csv file is empty or contains no columns to parse.")
	return dic

def calculate_average(project_name, coverage_choice, num_exp):
	dfs = []
	for i in range(num_exp):
		df= pd.read_csv(f'./_work/results/{project_name}/{coverage_choice}_data/{i}_{coverage_choice}_data.csv')
		df = df.drop('Profile Choice', axis=1)
		dfs.append(df) 

	# merge all 5 data and calculate mean
	merged_df = pd.concat(dfs).groupby(['Version'],sort=False, as_index=False).mean() 
	merged_df['#Files'] = merged_df['#Files'].astype(int)
	merged_df['LOC'] = merged_df['LOC'].astype(int)
	merged_df['#Class'] = merged_df['#Class'].astype(int)
	merged_df['#Method'] = merged_df['#Method'].astype(int)
	merged_df.to_csv(f'./_work/results/{project_name}/{coverage_choice}_data/average_data.csv', index=False)

# this function is used to calcuate the average result over n(5) runs, it also generates the comparison data,
# and the plotting the result as line plot
def calculate_average_ibjacoco(project_name, num_exp):
	dfs_ijacoco = []
	dfs_bjacoco = []
       
	for i in range(num_exp):
		df_ijacoco = pd.read_csv(f'./_work/results/{project_name}/ijacoco_data/{i}_ijacoco_data.csv')
		dfs_ijacoco.append(df_ijacoco) 

	# merge all 5 data and calculate mean
	merged_df_ijacoco = pd.concat(dfs_ijacoco).groupby(['Version', 'Profile Choice'],sort=False, as_index=False).mean() 

	for i in range(num_exp):
		df_bjacoco = pd.read_csv(f'./_work/results/{project_name}/bjacoco_data/{i}_bjacoco_data.csv')
		dfs_bjacoco.append(df_bjacoco) 
	merged_df_bjacoco = pd.concat(dfs_bjacoco).groupby(['Version', 'Profile Choice'],sort=False, as_index=False).mean()
       
	merged_df = pd.concat([merged_df_ijacoco, merged_df_bjacoco])
	comparison_df = comparison_calculate(merged_df_ijacoco, merged_df_bjacoco)	

	comparison_df.to_csv(f'./_work/results/{project_name}/comparison_data_average.csv', index=False)
	merged_df.to_csv(f'./_work/results/{project_name}/average_data.csv', index=False)

	draw_plot(merged_df_ijacoco, merged_df_bjacoco)
	plt.suptitle("ijacoco vs. bjacoco Average", fontsize=18, fontweight="bold")
	plt.savefig(f'./_work/results/{project_name}/plot_average.png', bbox_inches='tight')

# takes two dataframes as input, used by line_plot() to draw the plot 
def draw_plot(ijacoco_df, bjacoco_df):
		figure, axis = plt.subplots(2, 2,  figsize=(16, 8)) 
		figure.subplots_adjust(wspace=0.5, hspace=0.5)

		axis[0, 0].plot(bjacoco_df.index, bjacoco_df['Time'], label='bjacocop')
		axis[0, 0].plot(ijacoco_df.index, ijacoco_df['Time'], label='ijacocop', )
		axis[0, 0].set_title('Time')
		axis[0, 0].set_xlabel('Index')
		axis[0, 0].set_ylabel('Time')
		axis[0, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))

		axis[0, 1].plot(bjacoco_df.index, bjacoco_df['Instruction Coverage'], label='bjacocop', )
		axis[0, 1].plot(ijacoco_df.index, ijacoco_df['Instruction Coverage'], label='ijacocop', )
		axis[0, 1].set_title('Instruction Coverage')
		axis[0, 1].set_xlabel('Index')
		axis[0, 1].set_ylabel('Instruction Coverage')
		axis[0, 1].legend(loc='upper left', bbox_to_anchor=(1, 1))

		axis[1, 0].plot(bjacoco_df.index, bjacoco_df['Branch Coverage'], label='bjacocop')
		axis[1, 0].plot(ijacoco_df.index, ijacoco_df['Branch Coverage'], label='ijacocop')
		axis[1, 0].set_title('Branch Coverage')
		axis[1, 0].set_xlabel('Index')
		axis[1, 0].set_ylabel('Branch Coverage')
		axis[1, 0].legend(loc='upper left', bbox_to_anchor=(1, 1))

		axis[1, 1].plot(bjacoco_df.index, bjacoco_df['Line Coverage'], label='bjacocop')
		axis[1, 1].plot(ijacoco_df.index, ijacoco_df['Line Coverage'], label='ijacocop')
		axis[1, 1].set_title('Line Coverage')
		axis[1, 1].set_xlabel('Index')
		axis[1, 1].set_ylabel('Line Coverage')
		axis[1, 1].legend(loc='upper left', bbox_to_anchor=(1, 1))

# generates the line plot for comparing the metrics for ijacoco and bjacoco result
def line_plot(project_name: str, suffix: str):
	ijacoco_df = pd.read_csv(f'./_work/results/{project_name}/ijacoco_data/{suffix}_ijacoco_data.csv')
	bjacoco_df = pd.read_csv(f'./_work/results/{project_name}/bjacoco_data/{suffix}_bjacoco_data.csv')
	draw_plot(ijacoco_df, bjacoco_df)
	plt.suptitle(f"ijacoco vs. bjacoco #{suffix}", fontsize=18, fontweight="bold")
	plt.savefig(f'./_work/results/{project_name}/plot_{suffix}.png', bbox_inches='tight')


# takes two dataframes as input, used by coverage_difference() to calculate the difference between to coverage choice 
def comparison_calculate(ijacoco_df, bjacoco_df):
		columns = ['Version', 'Time', 'Instruction Coverage', 'Branch Coverage', 'Line Coverage']

		comparison_df = pd.DataFrame(columns=columns)

		comparison_df["Version"] = ijacoco_df["Version"]

		for metric in columns[1:]:
			comparison_df[metric] = pd.to_numeric(ijacoco_df[metric]) - pd.to_numeric(bjacoco_df[metric])
			# comparison_df[metric] = round((ijacoco_df[metric] - bjacoco_df[metric]), 4)
		return comparison_df

# calculates the difference between ijacoco and bjacoco data, and ouputs the comparison_data
def coverage_difference(project_name: str, suffix: str):
    ijacoco_df = pd.read_csv(f'./_work/results/{project_name}/ijacoco_data/{suffix}_ijacoco_data.csv')
    bjacoco_df = pd.read_csv(f'./_work/results/{project_name}/bjacoco_data/{suffix}_bjacoco_data.csv')
    
    comparison_df = comparison_calculate(ijacoco_df, bjacoco_df)
    comparison_df.to_csv(f'./_work/results/{project_name}/comparison_data_{suffix}.csv', index=False)