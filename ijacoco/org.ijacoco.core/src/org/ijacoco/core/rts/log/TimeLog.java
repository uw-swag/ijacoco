package org.ijacoco.core.rts.log;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import org.ijacoco.core.rts.Config;
import org.ijacoco.core.rts.Names;

/**
 * A simple time log for recording the execution time of different parts of the
 * code. The log for each thread and is stored in a separate, randomly numbered
 * file.
 */
public class TimeLog {

	private static String getThreadLogFile() {
		return Config.RTS_DIR_V + System.getProperty("file.separator")
				+ Names.TIME_LOG_FILE_NAME
				+ System.getProperty("file.separator")
				+ new Random(System.currentTimeMillis()).nextInt() + ".log";
	}

	private static ThreadLocal<PrintWriter> pw = new ThreadLocal<PrintWriter>();
	private static List<PrintWriter> pwList = new ArrayList<PrintWriter>();

	static {
		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				for (PrintWriter pw : pwList) {
					pw.close();
				}
			}
		});
	}

	/**
	 * Initializes the time log file for the current thread.
	 */
	public static void initLogFile() {
		try {
			File file = new File(getThreadLogFile());
			if (!file.getParentFile().exists()
					&& !file.getParentFile().mkdirs()) {
				System.err.println("Unable to create time log directory.");
				throw new RuntimeException();
			}
			pw.set(new PrintWriter(file));
			pwList.add(pw.get());
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}
	}

	/**
	 * Log a event to the time log file, appending the current timestamp in
	 * nanosecond.
	 *
	 * @param event
	 *            a short name of the event.
	 */
	public static final void log(String event) {
		if (pw.get() == null) {
			initLogFile();
		}
		pw.get().println(event + "@" + System.nanoTime());
		pw.get().flush();
	}
}
