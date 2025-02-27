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
package org.ijacoco.maven;

import java.io.IOException;
import java.util.List;
import java.util.Locale;

import org.apache.maven.doxia.siterenderer.Renderer;
import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugins.annotations.Component;
import org.apache.maven.plugins.annotations.Parameter;
import org.apache.maven.project.MavenProject;
import org.apache.maven.reporting.AbstractMavenReport;
import org.apache.maven.reporting.MavenReportException;
import org.ijacoco.core.rts.log.TimeLog;
import org.ijacoco.report.IReportGroupVisitor;
import org.ijacoco.report.IReportVisitor;

/**
 * Base class for creating a code coverage report for tests of a single project
 * in multiple formats (HTML, XML, and CSV).
 */
public abstract class AbstractReportMojo extends AbstractMavenReport {

	/**
	 * Encoding of the generated reports.
	 */
	@Parameter(property = "project.reporting.outputEncoding", defaultValue = "UTF-8")
	String outputEncoding;

	/**
	 * Name of the root node HTML report pages.
	 *
	 * @since 0.7.7
	 */
	@Parameter(defaultValue = "${project.name}")
	String title;

	/**
	 * Footer text used in HTML report pages.
	 *
	 * @since 0.7.7
	 */
	@Parameter
	String footer;

	/**
	 * Encoding of the source files.
	 */
	@Parameter(property = "project.build.sourceEncoding", defaultValue = "UTF-8")
	String sourceEncoding;

	/**
	 * A list of class files to include in the report. May use wildcard
	 * characters (* and ?). When not specified everything will be included.
	 */
	@Parameter
	List<String> includes;

	/**
	 * A list of class files to exclude from the report. May use wildcard
	 * characters (* and ?). When not specified nothing will be excluded.
	 */
	@Parameter
	List<String> excludes;

	/**
	 * Flag used to suppress execution.
	 */
	@Parameter(property = "ijacoco.skip", defaultValue = "false")
	boolean skip;

	/**
	 * Maven project.
	 */
	@Parameter(property = "project", readonly = true)
	MavenProject project;

	/**
	 * Doxia Site Renderer.
	 */
	@Component
	Renderer siteRenderer;

	public String getDescription(final Locale locale) {
		return getName(locale) + " Coverage Report.";
	}

	@Override
	public boolean isExternalReport() {
		return true;
	}

	@Override
	protected MavenProject getProject() {
		return project;
	}

	@Override
	protected Renderer getSiteRenderer() {
		return siteRenderer;
	}

	/**
	 * Returns the list of class files to include in the report.
	 *
	 * @return class files to include, may contain wildcard characters
	 */
	List<String> getIncludes() {
		return includes;
	}

	/**
	 * Returns the list of class files to exclude from the report.
	 *
	 * @return class files to exclude, may contain wildcard characters
	 */
	List<String> getExcludes() {
		return excludes;
	}

	@Override
	public boolean canGenerateReport() {
		if (skip) {
			getLog().info(
					"Skipping iJaCoCo execution because property ijacoco.skip is set.");
			return false;
		}
		if (!canGenerateReportRegardingDataFiles()) {
			getLog().info(
					"Skipping iJaCoCo execution due to missing execution data file.");
			return false;
		}
		if (!canGenerateReportRegardingClassesDirectory()) {
			getLog().info(
					"Skipping iJaCoCo execution due to missing classes directory.");
			return false;
		}
		return true;
	}

	abstract boolean canGenerateReportRegardingDataFiles();

	abstract boolean canGenerateReportRegardingClassesDirectory();

	/**
	 * This method is called when the report generation is invoked directly as a
	 * standalone Mojo.
	 */
	@Override
	public void execute() throws MojoExecutionException {
		if (!canGenerateReport()) {
			return;
		}
		TimeLog.log("report:beg");
		try {
			executeReport(Locale.getDefault());
		} catch (final MavenReportException e) {
			throw new MojoExecutionException("An error has occurred in "
					+ getName(Locale.ENGLISH) + " report generation.", e);
		}
		TimeLog.log("report:end");
	}

	@Override
	protected void executeReport(final Locale locale)
			throws MavenReportException {
		try {
			final ReportSupport support = new ReportSupport(getLog());
			loadExecutionData(support);
			addFormatters(support, locale);
			final IReportVisitor visitor = support.initRootVisitor();
			createReport(visitor, support);
			visitor.visitEnd();
		} catch (final IOException e) {
			throw new MavenReportException(
					"Error while creating report: " + e.getMessage(), e);
		}
	}

	abstract void loadExecutionData(final ReportSupport support)
			throws IOException;

	abstract void addFormatters(final ReportSupport support,
			final Locale locale) throws IOException;

	abstract void createReport(final IReportGroupVisitor visitor,
			final ReportSupport support) throws IOException;

}
