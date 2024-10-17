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
package org.ijacoco.agent.rt;

import org.ijacoco.agent.rt.internal.Agent;

/**
 * Entry point to access the iJaCoCo agent runtime.
 */
public final class RT {

	private RT() {
	}

	/**
	 * Returns the agent instance of the iJaCoCo runtime in this JVM.
	 *
	 * @return agent instance
	 * @throws IllegalStateException
	 *             if no Agent has been started yet
	 */
	public static IAgent getAgent() throws IllegalStateException {
		return Agent.getInstance();
	}

}
