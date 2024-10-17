/*******************************************************************************
 * Copyright (c) 2009, 2020 Mountainminds GmbH & Co. KG and Contributors
 * This program and the accompanying materials are made available under
 * the terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *    Brock Janiczak -initial API and implementation
 *
 *******************************************************************************/
package org.ijacoco.report.xml;

import java.io.IOException;
import java.io.OutputStream;
import java.util.Collection;
import java.util.List;

import org.ijacoco.core.coverage.analysis.IBundleCoverage;
import org.ijacoco.core.coverage.data.ExecutionData;
import org.ijacoco.core.coverage.data.SessionInfo;
import org.ijacoco.report.IReportGroupVisitor;
import org.ijacoco.report.IReportVisitor;
import org.ijacoco.report.ISourceFileLocator;
import org.ijacoco.report.internal.xml.ReportElement;
import org.ijacoco.report.internal.xml.XMLCoverageWriter;
import org.ijacoco.report.internal.xml.XMLGroupVisitor;

/**
 * Report formatter that creates a single XML file for a coverage session
 */
public class XMLFormatter {

	private String outputEncoding = "UTF-8";

	/**
	 * Sets the encoding used for generated XML document. Default is UTF-8.
	 *
	 * @param outputEncoding
	 *            XML output encoding
	 */
	public void setOutputEncoding(final String outputEncoding) {
		this.outputEncoding = outputEncoding;
	}

	/**
	 * Creates a new visitor to write a report to the given stream.
	 *
	 * @param output
	 *            output stream to write the report to
	 * @return visitor to emit the report data to
	 * @throws IOException
	 *             in case of problems with the output stream
	 */
	public IReportVisitor createVisitor(final OutputStream output)
			throws IOException {
		class RootVisitor implements IReportVisitor {

			private ReportElement report;
			private List<SessionInfo> sessionInfos;
			private XMLGroupVisitor groupVisitor;

			public void visitInfo(final List<SessionInfo> sessionInfos,
					final Collection<ExecutionData> executionData)
					throws IOException {
				this.sessionInfos = sessionInfos;
			}

			public void visitBundle(final IBundleCoverage bundle,
					final ISourceFileLocator locator) throws IOException {
				createRootElement(bundle.getName());
				XMLCoverageWriter.writeBundle(bundle, report);
			}

			public IReportGroupVisitor visitGroup(final String name)
					throws IOException {
				createRootElement(name);
				groupVisitor = new XMLGroupVisitor(report, name);
				return groupVisitor;
			}

			private void createRootElement(final String name)
					throws IOException {
				report = new ReportElement(name, output, outputEncoding);
				for (final SessionInfo i : sessionInfos) {
					report.sessioninfo(i);
				}
			}

			public void visitEnd() throws IOException {
				if (groupVisitor != null) {
					groupVisitor.visitEnd();
				}
				report.close();
			}
		}
		return new RootVisitor();
	}

}
