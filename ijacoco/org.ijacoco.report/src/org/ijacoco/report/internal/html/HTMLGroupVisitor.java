/*******************************************************************************
 * Copyright (c) 2009, 2020 Mountainminds GmbH & Co. KG and Contributors
 * This program and the accompanying materials are made available under
 * the terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *    Marc R. Hoffmann - initial API and implementation
 *
 *******************************************************************************/
package org.ijacoco.report.internal.html;

import java.io.IOException;

import org.ijacoco.core.coverage.analysis.IBundleCoverage;
import org.ijacoco.core.coverage.analysis.ICoverageNode;
import org.ijacoco.report.ISourceFileLocator;
import org.ijacoco.report.internal.AbstractGroupVisitor;
import org.ijacoco.report.internal.ReportOutputFolder;
import org.ijacoco.report.internal.html.page.BundlePage;
import org.ijacoco.report.internal.html.page.GroupPage;
import org.ijacoco.report.internal.html.page.NodePage;
import org.ijacoco.report.internal.html.page.ReportPage;

/**
 * Group visitor for HTML reports.
 */
public class HTMLGroupVisitor extends AbstractGroupVisitor {

	private final ReportOutputFolder folder;

	private final IHTMLReportContext context;

	private final GroupPage page;

	/**
	 * Create a new group handler.
	 *
	 * @param parent
	 *            optional hierarchical parent
	 * @param folder
	 *            base folder for this group
	 * @param context
	 *            settings context
	 * @param name
	 *            group name
	 */
	public HTMLGroupVisitor(final ReportPage parent,
			final ReportOutputFolder folder, final IHTMLReportContext context,
			final String name) {
		super(name);
		this.folder = folder;
		this.context = context;
		page = new GroupPage(total, parent, folder, context);
	}

	/**
	 * Returns the page rendered for this group.
	 *
	 * @return page for this group
	 */
	public NodePage<ICoverageNode> getPage() {
		return page;
	}

	@Override
	protected void handleBundle(final IBundleCoverage bundle,
			final ISourceFileLocator locator) throws IOException {
		final BundlePage bundlepage = new BundlePage(bundle, page, locator,
				folder.subFolder(bundle.getName()), context);
		bundlepage.render();
		page.addItem(bundlepage);
	}

	@Override
	protected AbstractGroupVisitor handleGroup(final String name)
			throws IOException {
		final HTMLGroupVisitor handler = new HTMLGroupVisitor(page,
				folder.subFolder(name), context, name);
		page.addItem(handler.getPage());
		return handler;
	}

	@Override
	protected void handleEnd() throws IOException {
		page.render();
	}

}
