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

import org.ijacoco.core.rts.RTS;
import org.ijacoco.core.rts.log.TimeLog;
import junit.framework.Test;
import junit.framework.TestResult;
import junit.framework.TestSuite;

public class JUnit3TestSuite implements Test {

	private Class<?> mTestClass;
	private TestSuite mTestSuite;

	public JUnit3TestSuite(Class<?> clz) {
		this.mTestClass = clz;
	}

	public int countTestCases() {
		return mTestSuite != null ? mTestSuite.countTestCases() : 0;
	}

	public void run(TestResult result) {
		if (RTS.inst().isClassAffected(mTestClass.getName())) {
			TimeLog.log("test:" + this.hashCode() + ":beg");
			JUnit3OutcomeListener outcomeListener = new JUnit3OutcomeListener();
			result.addListener(outcomeListener);
			try {
				RTS.inst().beginClassCoverage(mTestClass.getName());
				mTestSuite = new TestSuite(mTestClass);
				mTestSuite.run(result);
			} finally {
				TimeLog.log("test:" + this.hashCode() + ":end");
				RTS.inst().endClassCoverage(mTestClass.getName(),
						outcomeListener.isFailOrError());
			}
		}
	}
}
