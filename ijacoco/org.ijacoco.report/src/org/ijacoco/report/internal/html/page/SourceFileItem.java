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
package org.ijacoco.report.internal.html.page;

import org.ijacoco.core.coverage.analysis.ICoverageNode;
import org.ijacoco.core.coverage.analysis.ISourceFileCoverage;
import org.ijacoco.report.internal.ReportOutputFolder;
import org.ijacoco.report.internal.html.resources.Styles;
import org.ijacoco.report.internal.html.table.ITableItem;

/**
 * Table items representing a source file which cannot be linked.
 *
 */
final class SourceFileItem implements ITableItem {

	private final ICoverageNode node;

	SourceFileItem(final ISourceFileCoverage node) {
		this.node = node;
	}

	public String getLinkLabel() {
		return node.getName();
	}

	public String getLinkStyle() {
		return Styles.EL_SOURCE;
	}

	public String getLink(final ReportOutputFolder base) {
		return null;
	}

	public ICoverageNode getNode() {
		return node;
	}

}
