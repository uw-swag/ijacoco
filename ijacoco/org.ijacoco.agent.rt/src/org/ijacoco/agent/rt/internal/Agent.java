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
package org.ijacoco.agent.rt.internal;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.net.InetAddress;
import java.util.concurrent.Callable;
import org.ijacoco.agent.rt.IAgent;
import org.ijacoco.agent.rt.internal.output.FileOutput;
import org.ijacoco.agent.rt.internal.output.IAgentOutput;
import org.ijacoco.agent.rt.internal.output.NoneOutput;
import org.ijacoco.agent.rt.internal.output.TcpClientOutput;
import org.ijacoco.agent.rt.internal.output.TcpServerOutput;
import org.ijacoco.core.coverage.IJaCoCo;
import org.ijacoco.core.coverage.data.ExecutionDataStore;
import org.ijacoco.core.coverage.data.ExecutionDataWriter;
import org.ijacoco.core.coverage.runtime.AbstractRuntime;
import org.ijacoco.core.coverage.runtime.AgentOptions;
import org.ijacoco.core.coverage.runtime.AgentOptions.OutputMode;
import org.ijacoco.core.coverage.runtime.RuntimeData;
import org.ijacoco.core.coverage.tools.ExecFileLoader;

/**
 * The agent manages the life cycle of iJaCoCo runtime.
 */
public class Agent implements IAgent {

	private static Agent singleton;

	/**
	 * Returns a global instance which is already started. If the method is
	 * called the first time the instance is created with the given options.
	 *
	 * @param options
	 *            options to configure the instance
	 * @return global instance
	 * @throws Exception
	 *             in case something cannot be initialized
	 */
	public static synchronized Agent getInstance(final AgentOptions options)
			throws Exception {
		if (singleton == null) {
			final Agent agent = new Agent(options, IExceptionLogger.SYSTEM_ERR);
			agent.startup();
			Runtime.getRuntime().addShutdownHook(new Thread() {
				@Override
				public void run() {
					agent.shutdown();
				}
			});
			singleton = agent;
		}
		return singleton;
	}

	/**
	 * Returns a global instance which is already started. If a agent has not
	 * been initialized before this method will fail.
	 *
	 * @return global instance
	 * @throws IllegalStateException
	 *             if no Agent has been started yet
	 */
	public static synchronized Agent getInstance()
			throws IllegalStateException {
		if (singleton == null) {
			throw new IllegalStateException("iJaCoCo agent not started.");
		}
		return singleton;
	}

	private final AgentOptions options;

	private final IExceptionLogger logger;

	private final RuntimeData data;

	private IAgentOutput output;

	private Callable<Void> jmxRegistration;

	/**
	 * Creates a new agent with the given agent options.
	 *
	 * @param options
	 *            agent options
	 * @param logger
	 *            logger used by this agent
	 */
	Agent(final AgentOptions options, final IExceptionLogger logger) {
		this.options = options;
		this.logger = logger;
		this.data = new RuntimeData();
	}

	/**
	 * Returns the runtime data object created by this agent
	 *
	 * @return runtime data for this agent instance
	 */
	public RuntimeData getData() {
		return data;
	}

	/**
	 * Initializes this agent.
	 *
	 * @throws Exception
	 *             in case something cannot be initialized
	 */
	public void startup() throws Exception {
		try {
			String sessionId = options.getSessionId();
			if (sessionId == null) {
				sessionId = createSessionId();
			}
			data.setSessionId(sessionId);
			output = createAgentOutput();
			output.startup(options, data);
			if (options.getJmx()) {
				jmxRegistration = new JmxRegistration(this);
			}
		} catch (final Exception e) {
			logger.logExeption(e);
			throw e;
		}
	}

	/**
	 * Shutdown the agent again.
	 */
	public void shutdown() {
		try {
			// Used to merge the old data with the new data which is collected
			// after RTS.
			if (options.getMergeOnExit()) {
				ExecFileLoader loader = new ExecFileLoader();
				// TODO: currently we're loading the last version's exec file
				// from the output directory (/target/...), would it be better
				// to save it together with the RTS's cache (/.ekstazi/)?
				File execFile = new File(options.getDestfile())
						.getAbsoluteFile();
				loader.load(execFile);
				ExecutionDataStore lastExecutionStore = loader
						.getExecutionDataStore();
				ExecutionDataStore currentExecutionStore = data
						.getExecutionDataStore();
				currentExecutionStore.merge(lastExecutionStore);
			}
			if (options.getDumpOnExit()) {
				output.writeExecutionData(false);
			}
			output.shutdown();
			if (jmxRegistration != null) {
				jmxRegistration.call();
			}
		} catch (final Exception e) {
			logger.logExeption(e);
		}
	}

	/**
	 * Create output implementation as given by the agent options.
	 *
	 * @return configured controller implementation
	 */
	IAgentOutput createAgentOutput() {
		final OutputMode controllerType = options.getOutput();
		switch (controllerType) {
		case file:
			return new FileOutput();
		case tcpserver:
			return new TcpServerOutput(logger);
		case tcpclient:
			return new TcpClientOutput(logger);
		case none:
			return new NoneOutput();
		default:
			throw new AssertionError(controllerType);
		}
	}

	private String createSessionId() {
		String host;
		try {
			host = InetAddress.getLocalHost().getHostName();
		} catch (final Exception e) {
			// Also catch platform specific exceptions (like on Android) to
			// avoid bailing out here
			host = "unknownhost";
		}
		return host + "-" + AbstractRuntime.createRandomId();
	}

	// === IAgent Implementation ===

	public String getVersion() {
		return IJaCoCo.VERSION;
	}

	public String getSessionId() {
		return data.getSessionId();
	}

	public void setSessionId(final String id) {
		data.setSessionId(id);
	}

	public void reset() {
		data.reset();
	}

	public byte[] getExecutionData(final boolean reset) {
		final ByteArrayOutputStream buffer = new ByteArrayOutputStream();
		try {
			final ExecutionDataWriter writer = new ExecutionDataWriter(buffer);
			data.collect(writer, writer, reset);
		} catch (final IOException e) {
			// Must not happen with ByteArrayOutputStream
			throw new AssertionError(e);
		}
		return buffer.toByteArray();
	}

	public void dump(final boolean reset) throws IOException {
		output.writeExecutionData(reset);
	}

}
