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

import static org.ijacoco.core.rts.util.StringUtil.removeExtension;

import java.util.HashSet;
import java.util.Set;
import org.ijacoco.core.rts.data.Storer;
import org.ijacoco.core.rts.hash.Hasher;

class NameBasedCheck extends AbstractCheck {

	/** Affected set of classes */
	private final Set<String> mAffected;

	/** Extension for the file that stores dependencies */
	private final String mExtension;

	/**
	 * Constructor.
	 */
	public NameBasedCheck(Storer storer, Hasher hasher, String extension) {
		super(storer, hasher);
		this.mAffected = new HashSet<String>();
		this.mExtension = extension;
	}

	@Override
	public String includeAll(String fileName, String fileDir) {
		String className = removeExtension(fileName, mExtension);
		if (isAffected(fileDir, className, mExtension)) {
			mAffected.add(className);
		}
		return className;
	}

	@Override
	public void includeAffected(Set<String> affectedClasses) {
		affectedClasses.addAll(mAffected);
	}
}
