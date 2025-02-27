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

/**
 * <p>
 * Coverage calculation and analysis. The coverage information is calculated
 * with an {@link org.ijacoco.core.coverage.analysis.Analyzer} instance from
 * class files (target) and
 * {@linkplain org.ijacoco.core.coverage.data.IExecutionDataVisitor execution
 * data} (actual).
 * </p>
 *
 * <p>
 * The {@link org.ijacoco.core.coverage.analysis.CoverageBuilder} creates a
 * hierarchy of {@link org.ijacoco.core.coverage.analysis.ICoverageNode}
 * instances with the following
 * {@link org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType types}:
 * </p>
 *
 * <pre>
 * +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#GROUP Group} (optional)
 *     +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#BUNDLE Bundle}
 *         +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#PACKAGE Package}
 *             +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#SOURCEFILE Source File}
 *                 +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#CLASS Class}
 *                     +-- {@linkplain org.ijacoco.core.coverage.analysis.ICoverageNode.ElementType#METHOD Method}
 * </pre>
 */
package org.ijacoco.core.coverage.analysis;
