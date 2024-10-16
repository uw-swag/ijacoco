import pandas as pd
import seutil as su


def add_projects_data(work_dir, f, total_f, projects):
	# add project data to numbers_results.tex
	projects_data_file = work_dir / "paper_data" /"projects_data.csv"

	proj_df = pd.read_csv(
			projects_data_file,  
			dtype={
				"name": str, "URL": str, "Head": str, "#Ver": int, "#Files": int, "LOC": int, 
				"#Class": int, "#Method": int, "Time": float
				})
	
	proj_df = proj_df[proj_df["Project Name"].isin(projects)]
	for _, row in proj_df.iterrows():
		name = row["Project Name"].replace("_", "-")
		short_name = row["Project Name"].split("_")[1]
		f.append(su.latex.Macro(f"res-{name}-name", short_name))
		f.append(su.latex.Macro(f"res-{name}-url", row["URL"]))
		f.append(su.latex.Macro(f"res-{name}-head", row["Head"]))
		f.append(su.latex.Macro(f"res-{name}-num-ver", row["#Ver"]))
		f.append(su.latex.Macro(f"res-{name}-num-file", f"{row['#Files']:,d}"))
		f.append(su.latex.Macro(f"res-{name}-loc", f"{row['LOC']:,d}"))
		f.append(su.latex.Macro(f"res-{name}-num-class", f"{row['#Class']:,d}"))
		f.append(su.latex.Macro(f"res-{name}-num-method", f"{row['#Method']:,d}"))
		f.append(su.latex.Macro(f"res-{name}-time", f"{row['Time']:,.2f}"))

	sum_df = proj_df.sum()

	total_f.append(su.latex.Macro("num-revisions-per-repo", 51))
	total_f.append(su.latex.Macro("num-repo", f"{len(proj_df):,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-num-ver", f"{sum_df['#Ver']:,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-num-file", f"{sum_df['#Files']:,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-loc", f"{sum_df['LOC']:,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-num-test-class", f"{sum_df['#Class']:,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-num-test-method", f"{sum_df['#Method']:,d}"))
	total_f.append(su.latex.Macro("res-projects-sum-time", f"{sum_df['Time']:,.2f}"))

	f.save()
	total_f.save()

def add_retestall_ekstazi_data(choice, work_dir, f, total_f, projects):
	average_data_file = work_dir / "paper_data" / f"{choice}_avg_data.csv"
	avg_data_df = pd.read_csv(average_data_file)
	avg_data_df = avg_data_df[avg_data_df["Project Name"].isin(projects)]
	
	data_name = "retestall" if choice == "retestall" else "ekstazi"
	
	avg_time = avg_data_df["Time"].mean()
	sum_time = avg_data_df["Time"].sum()
	avg_total_time = avg_data_df["Total Time"].mean()
	sum_total_time = avg_data_df["Total Time"].sum()

	total_f.append(su.latex.Macro(f"{data_name}-sum-time", f"{sum_time:,.2f}"))
	total_f.append(su.latex.Macro(f"{data_name}-avg-time", f"{avg_time:,.2f}"))
	total_f.append(su.latex.Macro(f"{data_name}-avg-total-time", f"{avg_total_time:,.2f}"))
	total_f.append(su.latex.Macro(f"{data_name}-sum-total-time", f"{sum_total_time:,.2f}"))

	for _, row in avg_data_df.iterrows():
		name = row["Project Name"].replace("_", "-")
		f.append(su.latex.Macro(f"res-{name}-{data_name}-num-files", f"{int(row['#Files']):,d}"))
		f.append(su.latex.Macro(f"res-{name}-{data_name}-loc", f"{int(row['LOC']):,d}"))
		f.append(su.latex.Macro(f"res-{name}-{data_name}-num-class", f"{int(row['#Class']):,d}"))
		f.append(su.latex.Macro(f"res-{name}-{data_name}-num-method", f"{int(row['#Method']):,d}"))
		f.append(su.latex.Macro(f"res-{name}-{data_name}-time", f"{row['Time']:,.2f}"))
		f.append(su.latex.Macro(f"res-{name}-{data_name}-total-time", f"{row['Total Time']:,.2f}"))
		if data_name == "ekstazi":
			f.append(su.latex.Macro(f"res-{name}-{data_name}-selected-rate", f"{row['Selected Test Rate']*100:,.2f}"))

	if data_name == "ekstazi":
		total_f.append(su.latex.Macro("res-ekstazi-selected-test-rate-mean", 
					f"{avg_data_df['Selected Test Rate'].mean()*100:,.2f}"))
	f.save()
	total_f.save()

def add_coverage_data(work_dir, f):
	coverage_check_data = pd.read_csv(f"{work_dir}/paper_data/coverage_check.csv")
	# print(coverage_check_data)
	for _, row in coverage_check_data.iterrows():
		name = row["Project"].replace("_", "-")
		f.append(su.latex.Macro(f"{name}-coverage-diff", f"{row['|iJaCoCo Mean - bJaCoCo Mean|']:,.2f}"))
		f.append(su.latex.Macro(f"{name}-coverage-bjacoco-std", f"{row['bJaCoCo STD']:,.2f}"))
		exact_same = "\checkmark" if row['Exact Same'] else ""
		no_stat_sign_diff = "\checkmark" if row['No Stat Sign Diff'] else ""
		# within_std = "\checkmark" if row['Within STD'] else ""
		f.append(su.latex.Macro(f"{name}-coverage-exact-same", exact_same))
		f.append(su.latex.Macro(f"{name}-coverage-no-stat-sign-diff", no_stat_sign_diff))
		# f.append(su.latex.Macro(f"{name}-coverage-within-std", within_std))
		f.append(su.latex.Macro(f"res-{name}-ijacoco-coverage", f"{row['iJaCoCo Coverage Mean']:,.1f}"))
		f.append(su.latex.Macro(f"res-{name}-bjacoco-coverage", f"{row['bJaCoCo Coverage Mean']:,.1f}"))

	f.save()

def add_phase_data(work_dir, f):
	phase_data = pd.read_csv(f"{work_dir}/paper_data/phase_data.csv")
	# print(phase_data)
	for _, row in phase_data.iterrows():
		name = row["Project"].replace("_", "-")
		f.append(su.latex.Macro(f"res-{name}-phase-compile", f"{row['Time/compile']:,.2f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-analysis", f"{row['Time/analysis']:,.2f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-execution-collection", f"{row['Time/execution+collection']:,.2f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-report", f"{row['Time/report']:,.2f}"))

		# Add percentage data
		f.append(su.latex.Macro(f"res-{name}-phase-compile-percent", f"{row['Percentage/compile']:.1f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-analysis-percent", f"{row['Percentage/analysis']:.1f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-execution-collection-percent", f"{row['Percentage/execution+collection']:.1f}"))
		f.append(su.latex.Macro(f"res-{name}-phase-report-percent", f"{row['Percentage/report']:.1f}"))

	avg_compile = phase_data['Time/compile'].mean()
	avg_analysis = phase_data['Time/analysis'].mean()
	avg_execution_collection = phase_data['Time/execution+collection'].mean()
	avg_report = phase_data['Time/report'].mean()
	
	f.append(su.latex.Macro(f"res-phase-avg-compile", f"{avg_compile:,.2f}"))
	f.append(su.latex.Macro(f"res-phase-avg-analysis", f"{avg_analysis:,.2f}"))
	f.append(su.latex.Macro(f"res-phase-avg-execution-collection", f"{avg_execution_collection:,.2f}"))
	f.append(su.latex.Macro(f"res-phase-avg-report", f"{avg_report:,.2f}"))

	total_avg_time = avg_compile + avg_analysis + avg_execution_collection + avg_report

	# Add percentage data
	f.append(su.latex.Macro(f"res-phase-avg-compile-percent", f"{(avg_compile / total_avg_time) * 100:.1f}"))
	f.append(su.latex.Macro(f"res-phase-avg-analysis-percent", f"{(avg_analysis / total_avg_time) * 100:.1f}"))
	f.append(su.latex.Macro(f"res-phase-avg-execution-collection-percent", f"{(avg_execution_collection / total_avg_time) * 100:.1f}"))
	f.append(su.latex.Macro(f"res-phase-avg-report-percent", f"{(avg_report / total_avg_time) * 100:.1f}"))
	f.save()

def add_ibjacoco_data(work_dir, f, total_f, projects):

	ijacoco_file = work_dir / "paper_data" / "ijacoco_avg_data.csv"
	bjacoco_file = work_dir / "paper_data" / "bjacoco_avg_data.csv"
	ijacoco_df = pd.read_csv(ijacoco_file)
	ijacoco_df = ijacoco_df[ijacoco_df["Project Name"].isin(projects)]
	bjacoco_df = pd.read_csv(bjacoco_file)
	bjacoco_df = bjacoco_df[bjacoco_df["Project Name"].isin(projects)]
	
	total_f.append(su.latex.Macro("ijacoco-avg-time", f"{ijacoco_df['Time'].mean():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-sum-time", f"{ijacoco_df['Time'].sum():,.2f}"))
	total_f.append(su.latex.Macro("bjacoco-avg-time",  f"{bjacoco_df['Time'].mean():,.2f}"))
	total_f.append(su.latex.Macro("bjacoco-sum-time", f"{bjacoco_df['Time'].sum():,.2f}"))

	total_f.append(su.latex.Macro("ijacoco-avg-total-time", f"{ijacoco_df['Total Time'].mean():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-sum-total-time", f"{ijacoco_df['Total Time'].sum():,.2f}"))
	total_f.append(su.latex.Macro("bjacoco-avg-total-time", f"{bjacoco_df['Total Time'].mean():,.2f}"))
	total_f.append(su.latex.Macro("bjacoco-sum-total-time", f"{bjacoco_df['Total Time'].sum():,.2f}"))

	total_f.append(su.latex.Macro("ijacoco-avg-speedup", f"{ijacoco_df['Speedup'].mean():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-sum-speedup", f"{ijacoco_df['Speedup'].sum():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-max-speedup", f"{ijacoco_df['Speedup'].max():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-min-speedup", f"{ijacoco_df['Speedup'].min():,.2f}"))
	total_f.append(su.latex.Macro("ijacoco-cnt-positive-speedup", f"{sum(ijacoco_df['Speedup'] > 1):,d}"))
	total_f.append(su.latex.Macro("ijacoco-cnt-negative-speedup", f"{sum(ijacoco_df['Speedup'] <= 1):,d}"))
	total_f.append(su.latex.Macro("res-ijacoco-selected-test-rate-mean", 
							f"{ijacoco_df['Selected Test Rate'].mean():,.2f}"))

	combined_df = pd.concat([ijacoco_df, bjacoco_df], ignore_index=True)
	grouped_df = combined_df.groupby("Project Name")

	for proj_name, group in grouped_df:
		i_df = group[group["Coverage Choice"] == "ijacoco"]
		b_df = group[group["Coverage Choice"] == "bjacoco"]

		ijacoco_time = i_df["Time"].values[0]
		bjacoco_time = b_df["Time"].values[0]

		ijacoco_max_time = i_df["Max Time"].values[0]
		bjacoco_max_time = b_df["Max Time"].values[0]

		ijacoco_min_time = i_df["Min Time"].values[0]
		bjacoco_min_time = b_df["Min Time"].values[0]

		ijacoco_total_time = i_df["Total Time"].values[0]
		bjacoco_total_time = b_df["Total Time"].values[0]

		ijacoco_max_coverage = i_df["Max Line Coverage"].values[0]
		bjacoco_max_coverage = b_df["Max Line Coverage"].values[0]

		ijacoco_min_coverage =i_df["Min Line Coverage"].values[0]
		bjacoco_min_coverage = b_df["Min Line Coverage"].values[0]

		speedup = i_df["Speedup"].values[0]
		ijacoco_selected_test = i_df['Selected Test Rate'].values[0]

		proj_name = proj_name.replace("_", "-")

		# add average run time data to numbers_results.tex
		f.append(su.latex.Macro(f"res-{proj_name}-ijacoco-time", f"{ijacoco_time:,.2f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-bjacoco-time", f"{bjacoco_time:,.2f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-ibjacoco-speedup-time", f"{speedup:,.2f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-max-ijacoco-time", f"{ijacoco_max_time:,.2f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-min-ijacoco-time", f"{ijacoco_min_time:,.2f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-max-bjacoco-time", f"{bjacoco_max_time:,.2f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-min-bjacoco-time", f"{bjacoco_min_time:,.2f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-total-ijacoco-time", f"{ijacoco_total_time:,.2f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-total-bjacoco-time", f"{bjacoco_total_time:,.2f}"))

		if bjacoco_time != 0:
			ratio = ijacoco_time / bjacoco_time
			f.append(su.latex.Macro(f"res-{proj_name}-ratio-time", f"{ratio:,.2f}"))

		# add max/min line coverage data to numbers_results.tex
		f.append(su.latex.Macro(f"res-{proj_name}-ijacoco-max-coverage", f"{ijacoco_max_coverage:.1f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-bjacoco-max-coverage", f"{bjacoco_max_coverage:.1f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-ijacoco-min-coverage", f"{ijacoco_min_coverage:.1f}"))
		f.append(su.latex.Macro(f"res-{proj_name}-bjacoco-min-coverage", f"{bjacoco_min_coverage:.1f}"))

		f.append(su.latex.Macro(f"res-{proj_name}-ijacoco-selected-rate", f"{ijacoco_selected_test:,.2f}"))
	f.save()
	total_f.save()