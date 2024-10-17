package org.ijacoco.core.rts.util;

public class StringUtil {
	/**
	 * Removes extension (and preceding dot if present) from the given string.
	 *
	 * @param str
	 *            String from which to remove [.]extension
	 * @param ext
	 *            Extension to remove
	 * @return Original string if extension is not present, string without
	 *         [.]extension otherwise
	 */
	public static String removeExtension(String str, String ext) {
		if (!str.endsWith(ext)) {
			return str;
		}
		int index = str.lastIndexOf(ext);
		index = index <= 0 ? 1 : index;
		str = str.substring(0, index - 1);
		return str;
	}
}
