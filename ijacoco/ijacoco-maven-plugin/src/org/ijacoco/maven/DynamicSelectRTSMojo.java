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

package org.ijacoco.maven;

import java.io.File;
import java.util.Arrays;
import java.util.List;

import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugins.annotations.LifecyclePhase;
import org.apache.maven.plugins.annotations.Mojo;
import org.ijacoco.core.rts.Config;
import org.ijacoco.core.rts.agent.AgentLoader;
import org.ijacoco.core.rts.log.TimeLog;
import org.ijacoco.core.rts.maven.AbstractMojoInterceptor;

/**
 * Implements selection process and integrates with Surefire. This mojo does not
 * require any changes in configuration to any plugin used during the build. The
 * goal implemented here is an alternative to using "select" and "restore"
 * goals, which require some changes to Surefire configuration.
 */
@Mojo(name = "select", defaultPhase = LifecyclePhase.PROCESS_TEST_CLASSES)
public class DynamicSelectRTSMojo extends StaticSelectRTSMojo {

	public void execute() throws MojoExecutionException {
		if (getSkipme()) {
			getLog().info("RTS is skipped.");
			return;
		}
		if (getSkipTests()) {
			getLog().info("Tests are skipped.");
			return;
		}

		checkIfRTSDirCanBeCreated();

		TimeLog.log("select:beg");

		if (isRestoreGoalPresent()) {
			super.execute();
		} else {
			executeThis();
		}

		TimeLog.log("select:end");
	}

	// INTERNAL

	/**
	 * Checks if .rts directory can be created. For example, the problems can
	 * happen if there is no sufficient permission.
	 */
	private void checkIfRTSDirCanBeCreated() throws MojoExecutionException {
		File rtsDir = Config.createRootDir(parentdir);
		// If .rts does not exist and cannot be created, let them
		// know. (We also remove directory if successfully created.)
		if (!rtsDir.exists() && (!rtsDir.mkdirs() || !rtsDir.delete())) {
			throw new MojoExecutionException(
					"Cannot create RTS directory in " + parentdir);
		}
	}

	/**
	 * Implements 'select' that does not require changes to any existing plugin
	 * in configuration file(s).
	 */
	private void executeThis() throws MojoExecutionException {
		// Try to attach agent that will modify Surefire.
		if (AgentLoader.loadRTSAgent()) {
			// Prepare initial list of options and set property.
			System.setProperty(AbstractMojoInterceptor.ARGLINE_INTERNAL_PROP,
					prepareRTSOptions());
			// Find non affected classes and set property.
			List<String> nonAffectedClasses = computeNonAffectedClasses();
			System.setProperty(AbstractMojoInterceptor.EXCLUDES_INTERNAL_PROP,
					Arrays.toString(nonAffectedClasses.toArray(new String[0])));
		} else {
			throw new MojoExecutionException(
					"RTS cannot attach to the JVM, please specify RTS 'restore' explicitly.");
		}
	}

	/**
	 * Prepares option for RTS (mostly from pom configuration). Note that some
	 * other options (e.g., "mode" or path to the agent) are prepared when
	 * Surefire starts execution.
	 */
	private String prepareRTSOptions() {
		return "force.all=" + getForceall() + ",force.failing="
				+ getForcefailing() + "," + getRootDirOption()
				+ (getXargs() == null || getXargs().equals("") ? ""
						: "," + getXargs());
	}
}
