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
package org.ijacoco.core.coverage.data;

import org.ijacoco.core.coverage.tools.FileUtils;
import org.ijacoco.core.rts.Config;
import org.ijacoco.core.rts.Names;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * In-memory data store for execution data. The data can be added through its
 * {@link IExecutionDataVisitor} interface. If execution data is provided
 * multiple times for the same class the data is merged, i.e. a probe is marked
 * as executed if it is reported as executed at least once. This allows to merge
 * coverage date from multiple runs. A instance of this class is not thread
 * safe.
 */
public final class ExecutionDataStore implements IExecutionDataVisitor {

	private final Map<Long, ExecutionData> entries = new HashMap<Long, ExecutionData>();

	private final Set<String> names = new HashSet<String>();

	/**
	 * Merge the entries from the other store into this store. If the other
	 * execution data name is absent in the current store, then overwrite the
	 * other execution data to this store.
	 *
	 * @param other
	 *            the other execution data store that overwrites the current
	 *            store
	 */
	public void merge(ExecutionDataStore other) {
		File classesToOverwriteFile = new File(Config.RTS_DIR_V,
				Names.CLASS_URLS_TO_UPDATE_COVERAGE_DATA_FILE);
		if (classesToOverwriteFile.exists()) {
			mergeWithCoverageClassFile(classesToOverwriteFile, other);
			return;
		}
		Set<String> ignoredPreviousCoverageClasses = new HashSet<String>();
		for (ExecutionData executionData : entries.values()) {
			String className = executionData.getName();
			ignoredPreviousCoverageClasses.add(className);
		}
		for (ExecutionData otherExecutionData : other.entries.values()) {
			String otherClassName = otherExecutionData.getName();
			if (!ignoredPreviousCoverageClasses.contains(otherClassName)) {
				put(otherExecutionData);
			}
		}
	}

	private void mergeWithCoverageClassFile(File classesToOverwriteFile,
			ExecutionDataStore other) {
		Set<String> classesToOverwriteCoverage = (Set<String>) FileUtils
				.deserialize(classesToOverwriteFile);
		Set<String> ignoredPreviousCoverageClasses = new HashSet<String>();
		// Remove irrelevant coverage data
		for (Map.Entry<Long, ExecutionData> entry : entries.entrySet()) {
			String className = entry.getValue().getName();
			for (String classToOverwriteCoverage : classesToOverwriteCoverage) {
				if (classToOverwriteCoverage.endsWith(className)) {
					// We keep the coverage data for the current run
					ignoredPreviousCoverageClasses.add(className);
					break;
				}
			}
			// We should not remove execution data because a new class may not
			// appear in classesToOverwriteCoverage.
		}
		// Merge previous coverage data
		for (ExecutionData otherExecutionData : other.entries.values()) {
			String otherClassName = otherExecutionData.getName();
			if (ignoredPreviousCoverageClasses.contains(otherClassName)) {
				continue;
			}
			// If a class in the classesToOverwriteCoverage is not in the
			// current data (not executed), it means that the class is deleted
			// so we should ignore the previous data for the class.
			boolean shouldIgnore = false;
			for (String classToOverwriteCoverage : classesToOverwriteCoverage) {
				if (classToOverwriteCoverage.endsWith(otherClassName)) {
					shouldIgnore = true;
					break;
				}
			}
			if (shouldIgnore) {
				continue;
			}
			put(otherExecutionData);
		}
	}

	/**
	 * Adds the given {@link ExecutionData} object into the store. If there is
	 * already execution data with this same class id, this structure is merged
	 * with the given one.
	 *
	 * @param data
	 *            execution data to add or merge
	 * @throws IllegalStateException
	 *             if the given {@link ExecutionData} object is not compatible
	 *             to a corresponding one, that is already contained
	 * @see ExecutionData#assertCompatibility(long, String, int)
	 */
	public void put(final ExecutionData data) throws IllegalStateException {
		final Long id = Long.valueOf(data.getId());
		final ExecutionData entry = entries.get(id);
		if (entry == null) {
			entries.put(id, data);
			names.add(data.getName());
		} else {
			entry.merge(data);
		}
	}

	/**
	 * Subtracts the probes in the given {@link ExecutionData} object from the
	 * store. I.e. for all set probes in the given data object the corresponding
	 * probes in this store will be unset. If there is no execution data with id
	 * of the given data object this operation will have no effect.
	 *
	 * @param data
	 *            execution data to subtract
	 * @throws IllegalStateException
	 *             if the given {@link ExecutionData} object is not compatible
	 *             to a corresponding one, that is already contained
	 * @see ExecutionData#assertCompatibility(long, String, int)
	 */
	public void subtract(final ExecutionData data)
			throws IllegalStateException {
		final Long id = Long.valueOf(data.getId());
		final ExecutionData entry = entries.get(id);
		if (entry != null) {
			entry.merge(data, false);
		}
	}

	/**
	 * Subtracts all probes in the given execution data store from this store.
	 *
	 * @param store
	 *            execution data store to subtract
	 * @see #subtract(ExecutionData)
	 */
	public void subtract(final ExecutionDataStore store) {
		for (final ExecutionData data : store.getContents()) {
			subtract(data);
		}
	}

	/**
	 * Returns the {@link ExecutionData} entry with the given id if it exists in
	 * this store.
	 *
	 * @param id
	 *            class id
	 * @return execution data or <code>null</code>
	 */
	public ExecutionData get(final long id) {
		return entries.get(Long.valueOf(id));
	}

	/**
	 * Checks whether execution data for classes with the given name are
	 * contained in the store.
	 *
	 * @param name
	 *            VM name
	 * @return <code>true</code> if at least one class with the name is
	 *         contained.
	 */
	public boolean contains(final String name) {
		return names.contains(name);
	}

	/**
	 * Returns the coverage data for the class with the given identifier. If
	 * there is no data available under the given id a new entry is created.
	 *
	 * @param id
	 *            class identifier
	 * @param name
	 *            VM name of the class
	 * @param probecount
	 *            probe data length
	 * @return execution data
	 */
	public ExecutionData get(final Long id, final String name,
			final int probecount) {
		ExecutionData entry = entries.get(id);
		if (entry == null) {
			entry = new ExecutionData(id.longValue(), name, probecount);
			entries.put(id, entry);
			names.add(name);
		} else {
			entry.assertCompatibility(id.longValue(), name, probecount);
		}
		return entry;
	}

	/**
	 * Resets all execution data probes, i.e. marks them as not executed. The
	 * execution data objects itself are not removed.
	 */
	public void reset() {
		for (final ExecutionData executionData : this.entries.values()) {
			executionData.reset();
		}
	}

	/**
	 * Returns a collection that represents current contents of the store.
	 *
	 * @return current contents
	 */
	public Collection<ExecutionData> getContents() {
		return new ArrayList<ExecutionData>(entries.values());
	}

	/**
	 * Writes the content of the store to the given visitor interface.
	 *
	 * @param visitor
	 *            interface to write content to
	 */
	public void accept(final IExecutionDataVisitor visitor) {
		for (final ExecutionData data : getContents()) {
			visitor.visitClassExecution(data);
		}
	}

	// === IExecutionDataVisitor ===

	public void visitClassExecution(final ExecutionData data) {
		put(data);
	}
}
