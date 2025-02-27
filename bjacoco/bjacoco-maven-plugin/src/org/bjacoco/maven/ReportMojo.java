/*******************************************************************************
 * Copyright (c) 2009, 2020 Mountainminds GmbH & Co. KG and Contributors
 * This program and the accompanying materials are made available under
 * the terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *    Evgeny Mandrikov - initial API and implementation
 *
 *******************************************************************************/
package org.bjacoco.maven;

import java.io.File;
import java.io.IOException;
import java.util.Locale;

import org.apache.maven.plugins.annotations.LifecyclePhase;
import org.apache.maven.plugins.annotations.Mojo;
import org.apache.maven.plugins.annotations.Parameter;
import org.bjacoco.report.IReportGroupVisitor;

/**
 * Creates a code coverage report for tests of a single project in multiple
 * formats (HTML, XML, and CSV).
 *
 * @since 0.5.3
 */
@Mojo(name = "report", defaultPhase = LifecyclePhase.VERIFY, threadSafe = true)
public class ReportMojo extends AbstractReportMojo {

	/**
	 * Output directory for the reports. Note that this parameter is only
	 * relevant if the goal is run from the command line or from the default
	 * build lifecycle. If the goal is run indirectly as part of a site
	 * generation, the output directory configured in the Maven Site Plugin is
	 * used instead.
	 */
	@Parameter(defaultValue = "${project.reporting.outputDirectory}/bjacoco")
	private File outputDirectory;

	/**
	 * File with execution data.
	 */
	@Parameter(property = "bjacoco.dataFile", defaultValue = "${project.build.directory}/bjacoco.exec")
	private File dataFile;

	@Override
	boolean canGenerateReportRegardingDataFiles() {
		return dataFile.exists();
	}

	@Override
	boolean canGenerateReportRegardingClassesDirectory() {
		return new File(getProject().getBuild().getOutputDirectory()).exists();
	}

	@Override
	void loadExecutionData(final ReportSupport support) throws IOException {
		support.loadExecutionData(dataFile);
	}

	@Override
	void addFormatters(final ReportSupport support, final Locale locale)
			throws IOException {
		support.addAllFormatters(outputDirectory, outputEncoding, footer,
				locale);
	}

	@Override
	void createReport(final IReportGroupVisitor visitor,
			final ReportSupport support) throws IOException {
		support.processProject(visitor, title, getProject(), getIncludes(),
				getExcludes(), sourceEncoding);
	}

	@Override
	protected String getOutputDirectory() {
		return outputDirectory.getAbsolutePath();
	}

	@Override
	public void setReportOutputDirectory(final File reportOutputDirectory) {
		if (reportOutputDirectory != null && !reportOutputDirectory
				.getAbsolutePath().endsWith("bjacoco")) {
			outputDirectory = new File(reportOutputDirectory, "bjacoco");
		} else {
			outputDirectory = reportOutputDirectory;
		}
	}

	public String getOutputName() {
		return "bjacoco/index";
	}

	public String getName(final Locale locale) {
		return "bJaCoCo";
	}
}
