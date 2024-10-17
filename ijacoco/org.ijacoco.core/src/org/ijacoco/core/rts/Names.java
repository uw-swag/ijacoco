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

package org.ijacoco.core.rts;

/**
 * Shared constants.
 */
public final class Names {
	public static final String TOOL_NAME = "RTS";

	// Configuration.
	/** Configuration file name (in home/user directory) */
	public static final String RTS_CONFIG_FILE = ".ijacocorc";
	public static final String RTS_ROOT_DIR_NAME = ".ekstazi";

	public static final String CLASS_URLS_TO_UPDATE_COVERAGE_DATA_FILE = "cov_classes";

	/** Directory (inside root directory) for test results */
	public static final String TEST_RESULTS_DIR_NAME = "test-results";

	/** Directory (inside root directory) for instrumented files */
	public static final String INSTRUMENTED_CLASSES_DIR_NAME = "bank";

	// Packages.
	public static final String RTS_PACKAGE_BIN = "org.ijacoco.core.rts";
	public static final String RTS_PACKAGE_VM = "org/ijacoco/core/rts";
	public static final String iJACOCO_PACKAGE_BIN = "org.ijacoco";
	public static final String iJACOCO_PACKAGE_VM = "org/ijacoco";

	public static final String RTS_HASH_PACKAGE_BIN = "org.ijacoco.core.rts.hash";
	public static final String RTS_MONITOR_PACKAGE_BIN = "org.ijacoco.core.rts.monitor";

	public static final String JUNIT_FRAMEWORK_PACKAGE_BIN = "junit";
	public static final String JUNIT_FRAMEWORK_PACKAGE_VM = "junit";
	public static final String ORG_JUNIT_PACKAGE_BIN = "org.junit";
	public static final String ORG_JUNIT_PACKAGE_VM = "org/junit";
	public static final String ORG_HAMCREST_BIN = "org.hamcrest";
	public static final String ORG_HAMCREST_VM = "org/hamcrest";
	public static final String ORG_APACHE_MAVEN_BIN = "org.apache.maven";
	public static final String ORG_APACHE_MAVEN_VM = "org/apache/maven";

	// Classes.
	public static final String CONFIG_BIN = RTS_PACKAGE_BIN + "." + "Config";
	public static final String COVERAGE_MONITOR_BIN = "org.ijacoco.core.rts.monitor.CoverageMonitor";
	public static final String COVERAGE_MONITOR_VM = "org/ijacoco/core/rts/monitor/CoverageMonitor";
	public static final String DYNAMIC_AGENT_BIN = "org.ijacoco.core.rts.instrument.DynamicAgent";
	public static final String RTS_CLASSLOADER_BIN = "org.ijacoco.core.rts.cl.RTSClassLoader";

	// Maven classes.
	public static final String ABSTRACT_SUREFIRE_MOJO_CLASS_VM = "org.apache.maven.plugin.surefire.AbstractSurefireMojo";
	public static final String SUREFIRE_PLUGIN_VM = "org/apache/maven/plugin/surefire/SurefirePlugin";
	public static final String FAILSAFE_PLUGIN_VM = "org/apache/maven/plugin/failsafe/IntegrationTestMojo";
	public static final String TESTMOJO_VM = "org/scalatest/tools/maven/TestMojo";
	// ScalaTest related classes.
	public static final String SCALATEST_CFT_BIN = "org.ijacoco.core.rts.scalatest.ScalaTestCFT";

	// Names of several files used by the tool.
	public static final String RUN_INFO_FILE_NAME = "run.info";
	public static final String TIME_LOG_FILE_NAME = "time-logs";
	public static final String VERBOSE_FILE_NAME = "verbose.output";
	public static final String HASHER_CACHE_FILE_NAME = "hasher-cache.txt";
	public static final String META_FILE_NAME = "META";

	/** Names of all files used by the tool */
	public static final String[] ALL_FILE_NAMES = { RUN_INFO_FILE_NAME,
			TIME_LOG_FILE_NAME, VERBOSE_FILE_NAME, HASHER_CACHE_FILE_NAME,
			META_FILE_NAME, };
}
