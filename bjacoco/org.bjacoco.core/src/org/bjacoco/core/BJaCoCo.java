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
package org.bjacoco.core;

import java.util.ResourceBundle;

/**
 * Static Meta information about JaCoCo.
 */
public final class BJaCoCo {

	/** Qualified build version of the JaCoCo core library. */
	public static final String VERSION;

	/** Absolute URL of the current JaCoCo home page */
	public static final String HOMEURL;

	/** Name of the runtime package of this build */
	public static final String RUNTIMEPACKAGE;

	static {
		final ResourceBundle bundle = ResourceBundle
				.getBundle("org.bjacoco.core.bjacoco");
		VERSION = bundle.getString("VERSION");
		HOMEURL = bundle.getString("HOMEURL");
		RUNTIMEPACKAGE = bundle.getString("RUNTIMEPACKAGE");
	}

	private BJaCoCo() {
	}

}
