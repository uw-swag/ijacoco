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

package org.ijacoco.core.rts.log;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

import org.ijacoco.core.rts.Config;

/**
 * Simple logging facility.
 */
public final class Log {

	private static final String DEBUG_TEXT = "RTS_Debug";
	private static final String ERROR_TEXT = "RTS_Error";
	private static final String WARN_TEXT = "RTS_Warn";
	private static final String CONF_TEXT = "RTS_Conf";

	private static PrintWriter pwScreen;
	private static PrintWriter pwFile;
	private static Path debugDir;

	public static void initScreen() {
		init(true, false, null, null);
	}

	public static void init(boolean printToScreen, boolean printToFile,
			String logFileName, String debugDirName) {
		if (printToScreen) {
			pwScreen = new PrintWriter(System.err);
		}
		if (printToFile) {
			try {
				File file = new File(logFileName);
				if (!file.getParentFile().exists()
						&& !file.getParentFile().mkdirs()) {
					w("Was unable to create log file");
					return;
				}
				pwFile = new PrintWriter(file);
				Runtime.getRuntime().addShutdownHook(new Thread() {
					@Override
					public void run() {
						pwFile.close();
					}
				});

			} catch (FileNotFoundException ex) {
				ex.printStackTrace();
			}

			File debugDirFile = new File(debugDirName);
			debugDirFile.mkdirs();
			debugDir = debugDirFile.toPath();
		}
	}

	/**
	 * Debugging.
	 */
	public static final void d(Object... messages) {
		if (Config.DEBUG_V) {
			print(DEBUG_TEXT + getPrefix() + ": ");
			for (int i = 0; i < messages.length; i++) {
				print(messages[i]);
				if (i != messages.length - 1) {
					print(" ");
				}
			}
			println(".");
		}
	}

	/**
	 * Debugging.
	 */
	public static final void d(String msg, int val) {
		if (Config.DEBUG_V) {
			d(msg, Integer.toString(val));
		}
	}

	/**
	 * Checks if the debug directory is set.
	 */
	public static final boolean hasDebugDir() {
		return debugDir != null;
	}

	/**
	 * Gets the path to debug directory (to dump files, etc.). Should first
	 * check {@link #hasDebugDir()}.
	 */
	public static final Path getDebugDir() {
		return debugDir;
	}

	/**
	 * Error during initialization (e.g., configuration error).
	 *
	 * @param msg
	 *            Message to be reported.
	 */
	public static final void e(String msg) {
		println(ERROR_TEXT + getPrefix() + ": " + msg);
	}

	public static final void e(String msg, Exception ex) {
		e(msg);
		if (Config.DEBUG_V) {
			ex.printStackTrace();
		}
	}

	/**
	 * Something may affect performance but not correctness.
	 */
	public static final void w(String msg) {
		println(WARN_TEXT + getPrefix() + ": " + msg);
	}

	/**
	 * Printing configuration options.
	 */
	public static final void c(String msg) {
		if (msg.replaceAll("\\s+", "").equals("")) {
			println(CONF_TEXT + getPrefix());
		} else {
			println(CONF_TEXT + getPrefix() + ": " + msg);
		}
	}

	public static final void c(Object key, Object value) {
		if (key.equals("") && value.equals("")) {
			c("");
		} else {
			c(key + " = " + value);
		}
	}

	private static final String getPrefix() {
		StringBuilder sb = new StringBuilder();
		sb.append("[");
		// current time
		DateTimeFormatter dtFmt = DateTimeFormatter.ofPattern("HH:mm:ss:SSSS");
		sb.append(dtFmt.format(LocalDateTime.now()));
		sb.append("|");
		// thread id
		sb.append(Thread.currentThread().getId());
		sb.append("]");

		sb.append(" ");
		return sb.toString();
	}

	private static void print(Object s) {
		if (pwScreen != null) {
			pwScreen.print(s);
			pwScreen.flush();
		}
		if (pwFile != null) {
			pwFile.print(s);
			pwFile.flush();
		}
	}

	private static void println(Object s) {
		if (pwScreen != null) {
			pwScreen.println(s);
			pwScreen.flush();
		}
		if (pwFile != null) {
			pwFile.println(s);
			pwFile.flush();
		}
	}
}
