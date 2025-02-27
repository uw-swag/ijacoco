/*
 * Copyright 2014-present Milos Gligoric
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.ijacoco.core.rts.junit;

import org.junit.runner.Description;
import org.junit.runner.Runner;
import org.junit.runner.notification.RunNotifier;

/**
 * Provides support to check if a class is affected.
 */
class AffectingRunner extends Runner {
	/** Class being run */
	private final Class<?> mTestClass;

	/**
	 * Constructor.
	 */
	public AffectingRunner(Class<?> testClass) {
		mTestClass = testClass;
	}

	@Override
	public void run(RunNotifier notifier) {
		// We decided not to tell the world that things are ignored.
		// notifier.fireTestIgnored(getDescription());
	}

	@Override
	public Description getDescription() {
		return Description.createSuiteDescription(mTestClass);
	}
}
