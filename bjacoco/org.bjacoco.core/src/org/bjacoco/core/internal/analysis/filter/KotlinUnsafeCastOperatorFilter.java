/*******************************************************************************
 * Copyright (c) 2009, 2020 Mountainminds GmbH & Co. KG and Contributors
 * This program and the accompanying materials are made available under
 * the terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 *
 * Contributors:
 *    Evgeny Mandrikov - initial API and implementation
 *
 *******************************************************************************/
package org.bjacoco.core.internal.analysis.filter;

import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.JumpInsnNode;
import org.objectweb.asm.tree.LdcInsnNode;
import org.objectweb.asm.tree.MethodNode;

/**
 * Filters branch in bytecode that Kotlin compiler generates for "unsafe" cast
 * operator.
 */
public final class KotlinUnsafeCastOperatorFilter implements IFilter {

	private static final String KOTLIN_TYPE_CAST_EXCEPTION = "kotlin/TypeCastException";

	public void filter(final MethodNode methodNode,
			final IFilterContext context, final IFilterOutput output) {
		final Matcher matcher = new Matcher();
		for (final AbstractInsnNode i : methodNode.instructions) {
			matcher.match(i, output);
		}
	}

	private static class Matcher extends AbstractMatcher {
		public void match(final AbstractInsnNode start,
				final IFilterOutput output) {

			if (Opcodes.IFNONNULL != start.getOpcode()) {
				return;
			}
			cursor = start;

			nextIsType(Opcodes.NEW, KOTLIN_TYPE_CAST_EXCEPTION);
			nextIs(Opcodes.DUP);
			nextIs(Opcodes.LDC);
			if (cursor == null) {
				return;
			}
			final LdcInsnNode ldc = (LdcInsnNode) cursor;
			if (!(ldc.cst instanceof String && ((String) ldc.cst)
					.startsWith("null cannot be cast to non-null type"))) {
				return;
			}
			nextIsInvoke(Opcodes.INVOKESPECIAL, KOTLIN_TYPE_CAST_EXCEPTION,
					"<init>", "(Ljava/lang/String;)V");
			nextIs(Opcodes.ATHROW);
			if (cursor == null) {
				return;
			}
			if (cursor.getNext() != ((JumpInsnNode) start).label) {
				return;
			}

			output.ignore(start, cursor);
		}
	}

}
