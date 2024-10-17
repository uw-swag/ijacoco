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
package org.ijacoco.report.internal.html.table;

import java.io.IOException;
import java.util.Comparator;
import java.util.List;

import org.ijacoco.core.coverage.analysis.ICoverageNode;
import org.ijacoco.report.internal.ReportOutputFolder;
import org.ijacoco.report.internal.html.HTMLElement;
import org.ijacoco.report.internal.html.resources.Resources;

/**
 * Column for the item label. The implementation is stateless, instances might
 * be used in parallel.
 */
public class LabelColumn implements IColumnRenderer {

	private static final Comparator<ITableItem> COMPARATOR = new Comparator<ITableItem>() {
		public int compare(final ITableItem i1, final ITableItem i2) {
			return i1.getLinkLabel().compareToIgnoreCase(i2.getLinkLabel());
		}
	};

	public boolean init(final List<? extends ITableItem> items,
			final ICoverageNode total) {
		return true;
	}

	public void footer(final HTMLElement td, final ICoverageNode total,
			final Resources resources, final ReportOutputFolder base)
			throws IOException {
		td.text("Total");
	}

	public void item(final HTMLElement td, final ITableItem item,
			final Resources resources, final ReportOutputFolder base)
			throws IOException {
		td.a(item, base);
	}

	public Comparator<ITableItem> getComparator() {
		return COMPARATOR;
	}

}
