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

package org.ijacoco.core.rts.check;

import java.util.Set;
import org.ijacoco.core.rts.data.RegData;
import org.ijacoco.core.rts.data.Storer;
import org.ijacoco.core.rts.hash.Hasher;

abstract class AbstractCheck {

	/** Storer */
	protected final Storer mStorer;

	/** Hasher */
	protected final Hasher mHasher;

	/**
	 * Constructor.
	 */
	public AbstractCheck(Storer storer, Hasher hasher) {
		this.mStorer = storer;
		this.mHasher = hasher;
	}

	public abstract String includeAll(String fileName, String fileDir);

	public abstract void includeAffected(Set<String> affectedClasses);

	protected boolean isAffected(String dirName, String className,
			String extensionName) {
		return isAffected(mStorer.load(dirName, className, extensionName));
	}

	protected boolean isAffected(Set<RegData> regData) {
		return regData == null || regData.size() == 0
				|| hasHashChanged(regData);
	}

	/**
	 * Check if any element of the given set has changed.
	 */
	private boolean hasHashChanged(Set<RegData> regData) {
		for (RegData el : regData) {
			if (hasHashChanged(mHasher, el)) {
				return true;
			}
		}
		return false;
	}

	/**
	 * Check if the given datum has changed using the given hasher.
	 */
	public static boolean hasHashChanged(Hasher hasher, RegData regDatum) {
		String urlExternalForm = regDatum.getURLExternalForm();
		// Check hash.
		String newHash = hasher.hashURL(urlExternalForm);
		return !newHash.equals(regDatum.getHash());
	}
}
