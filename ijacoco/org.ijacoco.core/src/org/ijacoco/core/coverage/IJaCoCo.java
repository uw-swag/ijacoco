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
package org.ijacoco.core.coverage;

import java.util.ResourceBundle;

/**
 * Static Meta information about iJaCoCo.
 */
public final class IJaCoCo {

	/** Qualified build version of the iJaCoCo core library. */
	public static final String VERSION;

	/** Absolute URL of the current iJaCoCo home page */
	public static final String HOMEURL;

	/** Name of the runtime package of this build */
	public static final String RUNTIMEPACKAGE;

	static {
		final ResourceBundle bundle = ResourceBundle
				.getBundle("org.ijacoco.core.coverage.ijacoco");
		VERSION = bundle.getString("VERSION");
		HOMEURL = bundle.getString("HOMEURL");
		RUNTIMEPACKAGE = bundle.getString("RUNTIMEPACKAGE");
	}

	private IJaCoCo() {
	}

}
