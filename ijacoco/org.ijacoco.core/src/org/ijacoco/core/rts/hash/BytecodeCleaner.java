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

package org.ijacoco.core.rts.hash;

import org.ijacoco.core.rts.util.FileUtil;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import org.ijacoco.core.rts.asm.AnnotationVisitor;
import org.ijacoco.core.rts.asm.ClassReader;
import org.ijacoco.core.rts.asm.ClassVisitor;
import org.ijacoco.core.rts.asm.FieldVisitor;
import org.ijacoco.core.rts.asm.Handle;
import org.ijacoco.core.rts.asm.Label;
import org.ijacoco.core.rts.asm.MethodVisitor;
import org.ijacoco.core.rts.asm.Opcodes;
import org.ijacoco.core.rts.asm.Type;

/**
 * Removes debug info from a class file. Visits a class file and keeps only the
 * most relevant parts of it (for hashing). For example, this class ignores
 * constant pool (and the order of constants in the pool).
 */
public final class BytecodeCleaner {

	/** Used ASM API version */
	private static final int ASM_API_VERSION = Opcodes.ASM5;

	/** "FILTERED" string used for filtered classes */
	private static final byte[] FILTERED_BYTECODE = { 70, 73, 76, 84, 69, 82,
			69, 68, };

	/**
	 * Filters for classes, methods, and fields.
	 */
	public static class Filter {
		public boolean filterClass(int version, int access, String name,
				String signature, String superName, String[] interfaces) {
			return false;
		}

		public boolean filterField(int access, String name, String desc,
				String signature, Object value) {
			return false;
		}

		public boolean filterMethod(int access, String name, String desc,
				String signature, String[] exceptions) {
			return false;
		}
	}

	private static final class CleanClass extends ClassVisitor {
		/** Method cleaner */
		private final CleanMethod mCleanMethod;

		/** Field cleaner */
		private final CleanField mCleanField;

		/** Annotation cleaner */
		private final CleanAnnotation mCleanAnnotation;

		/** Stream for the resulting bytes */
		private final DataOutputStream mBytes;

		/** Specifies classes to filter */
		private final Filter filter;

		/** True after visit if this class should be ignored */
		private boolean isFiltered;

		/**
		 * Constructor.
		 *
		 * @param dos
		 *            Bytes that are preserved.
		 */
		public CleanClass(DataOutputStream dos) {
			super(ASM_API_VERSION);
			this.mBytes = dos;
			this.mCleanAnnotation = new CleanAnnotation(dos);
			this.mCleanMethod = new CleanMethod(dos, mCleanAnnotation);
			this.mCleanField = new CleanField(dos, mCleanAnnotation);
			this.filter = new Filter();
		}

		public boolean isFiltered() {
			return isFiltered;
		}

		private void writeString(String s) {
			if (s != null) {
				try {
					mBytes.writeUTF(s);
				} catch (IOException ex) {
					// never
				}
			}
		}

		@Override
		public void visit(int version, int access, String name,
				String signature, String superName, String[] interfaces) {
			if (filter.filterClass(version, access, name, signature, superName,
					interfaces)) {
				isFiltered = true;
			}
			try {
				mBytes.writeInt(version);
				mBytes.writeInt(access);
				writeString(name);
				writeString(superName);
				if (interfaces != null) {
					for (String el : interfaces) {
						writeString(el);
					}
				}
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public AnnotationVisitor visitAnnotation(String desc, boolean visible) {
			if (visible) {
				writeString(desc);
				// Interesting only if annotation is visible.
				return mCleanAnnotation;
			} else {
				return null;
			}
		}

		// Ignore non standard attributes.
		// public visitAttribute(Attribute attr)

		// Nothing to do at the end of the visit.
		// public visitEnd()

		@Override
		public FieldVisitor visitField(int access, String name, String desc,
				String signature, Object value) {
			if (filter.filterField(access, name, desc, signature, value)) {
				isFiltered = true;
			}
			try {
				mBytes.writeInt(access);
				writeString(name);
				writeString(desc);
				writeString(signature);
				if (value != null) {
					if (value instanceof Integer) {
						mBytes.writeInt((Integer) value);
					} else if (value instanceof Float) {
						mBytes.writeFloat((Float) value);
					} else if (value instanceof Long) {
						mBytes.writeLong((Long) value);
					} else if (value instanceof Double) {
						mBytes.writeDouble((Double) value);
					} else if (value instanceof String) {
						writeString((String) value);
					}
				}
			} catch (IOException ex) {
				// never
			}
			return mCleanField;
		}

		@Override
		public void visitInnerClass(String name, String outerName,
				String innerName, int access) {
			try {
				writeString(name);
				writeString(outerName);
				writeString(innerName);
				mBytes.writeInt(access);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public MethodVisitor visitMethod(int access, String name, String desc,
				String signature, String[] exceptions) {
			if (filter.filterMethod(access, name, desc, signature,
					exceptions)) {
				isFiltered = true;
			}
			try {
				mBytes.writeInt(access);
				writeString(name);
				writeString(desc);
				writeString(signature);
				if (exceptions != null) {
					for (String el : exceptions) {
						writeString(el);
					}
				}
			} catch (IOException ex) {
				// never
			}
			return mCleanMethod;
		}

		@Override
		public void visitOuterClass(String owner, String name, String desc) {
			writeString(owner);
			writeString(name);
			writeString(desc);
		}

		// No need to visit sources as they do not change semantic.
		// public void visitSource()
	}

	private static final class CleanMethod extends MethodVisitor {
		/** Stream for the resulting bytes */
		private final DataOutputStream mBytes;

		/** Annotation cleaner */
		private final CleanAnnotation mCleanAnnotation;

		/** Next id for label; we assign unique id to each label */
		private int nextLabel;

		/**
		 * Constructor.
		 *
		 * @param baos
		 *            Stream to save the resulting bytes.
		 * @param cleanAnnotation
		 *            Annotation cleaner.
		 */
		public CleanMethod(DataOutputStream baos,
				CleanAnnotation cleanAnnotation) {
			super(ASM_API_VERSION);
			this.mBytes = baos;
			this.mCleanAnnotation = cleanAnnotation;
		}

		private void writeString(String s) {
			if (s != null) {
				try {
					mBytes.writeUTF(s);
				} catch (IOException ex) {
					// never
				}
			}
		}

		private void writeLabel(Label label) {
			// If extra info associated with the label is null, it means that
			// this label is not seen previously. We assign new unique id for
			// new labels.
			if (label.info == null) {
				label.info = nextLabel++;
			}
			try {
				mBytes.writeInt((Integer) label.info);
			} catch (IOException e) {
				// never
			}
		}

		@Override
		public AnnotationVisitor visitAnnotation(String desc, boolean visible) {
			if (visible) {
				writeString(desc);
				return mCleanAnnotation;
			} else {
				return null;
			}
		}

		@Override
		public AnnotationVisitor visitAnnotationDefault() {
			return mCleanAnnotation;
		}

		// Ignore non standard attributes.
		// public void visitAttribute(Attribute attr)

		// Nothing to do at the beginning.
		// public void visitCode()

		// Nothing to do at the end.
		// public void visitEnd()

		@Override
		public void visitFieldInsn(int opcode, String owner, String name,
				String desc) {
			try {
				mBytes.writeInt(opcode);
				writeString(owner);
				writeString(name);
				writeString(desc);
			} catch (IOException ex) {
				// never
			}
		}

		// No need to visit frames.
		// public void visitFrame()

		@Override
		public void visitIincInsn(int var, int increment) {
			try {
				mBytes.writeInt(var);
				mBytes.writeInt(increment);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitInsn(int opcode) {
			try {
				mBytes.writeInt(opcode);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitIntInsn(int opcode, int operand) {
			try {
				mBytes.writeInt(opcode);
				mBytes.writeInt(operand);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitInvokeDynamicInsn(String name, String desc, Handle bsm,
				Object... bsmArgs) {
			try {
				writeString(name);
				writeString(desc);
				writeString(bsm.toString());
				for (Object el : bsmArgs) {
					if (el instanceof Integer) {
						mBytes.writeInt((Integer) el);
					} else if (el instanceof Float) {
						mBytes.writeFloat((Float) el);
					} else if (el instanceof Long) {
						mBytes.writeLong((Long) el);
					} else if (el instanceof Double) {
						mBytes.writeDouble((Double) el);
					} else if (el instanceof String) {
						writeString((String) el);
					} else if (el instanceof Type || el instanceof Handle) {
						writeString(el.toString());
					}
				}
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitJumpInsn(int opcode, Label label) {
			try {
				mBytes.writeInt(opcode);
				writeLabel(label);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitLabel(Label label) {
			writeLabel(label);
		}

		@Override
		public void visitLdcInsn(Object cst) {
			try {
				if (cst instanceof Integer) {
					mBytes.writeInt((Integer) cst);
				} else if (cst instanceof Float) {
					mBytes.writeFloat((Float) cst);
				} else if (cst instanceof Long) {
					mBytes.writeLong((Long) cst);
				} else if (cst instanceof Double) {
					mBytes.writeDouble((Double) cst);
				} else if (cst instanceof String) {
					writeString((String) cst);
				} else if (cst instanceof Type) {
					int sort = ((Type) cst).getSort();
					if (sort == Type.OBJECT || sort == Type.ARRAY
							|| sort == Type.METHOD) {
						writeString(cst.toString());
					} else {
						throw new RuntimeException();
					}
				} else if (cst instanceof Handle) {
					writeString(cst.toString());
				} else {
					throw new RuntimeException();
				}
			} catch (IOException ex) {
				// never
			}
		}

		// Ignore line numbers as they do not change semantic.
		// public void visitLineNumber()

		@Override
		public void visitLocalVariable(String name, String desc,
				String signature, Label start, Label end, int index) {
			try {
				writeString(name);
				writeString(desc);
				writeString(signature);
				writeLabel(start);
				writeLabel(end);
				mBytes.writeInt(index);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitLookupSwitchInsn(Label dflt, int[] keys,
				Label[] labels) {
			try {
				writeLabel(dflt);
				for (int el : keys) {
					mBytes.writeInt(el);
				}
				for (Label el : labels) {
					writeLabel(el);
				}
			} catch (IOException ex) {
				// never
			}
		}

		// No need to visit max values for locals.
		// public void visitMaxs()

		@Override
		public void visitMethodInsn(int opcode, String owner, String name,
				String desc, boolean itf) {
			try {
				mBytes.writeInt(opcode);
				writeString(owner);
				writeString(name);
				writeString(desc);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitMultiANewArrayInsn(String desc, int dims) {
			try {
				writeString(desc);
				mBytes.writeInt(dims);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public AnnotationVisitor visitParameterAnnotation(int parameter,
				String desc, boolean visible) {
			if (visible) {
				try {
					mBytes.writeInt(parameter);
					writeString(desc);
				} catch (IOException ex) {
					// never
				}
				return mCleanAnnotation;
			} else {
				return null;
			}
		}

		@Override
		public void visitTableSwitchInsn(int min, int max, Label dflt,
				Label... labels) {
			try {
				mBytes.writeInt(min);
				mBytes.writeInt(max);
				writeLabel(dflt);
				for (Label el : labels) {
					writeLabel(el);
				}
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitTryCatchBlock(Label start, Label end, Label handler,
				String type) {
			writeLabel(start);
			writeLabel(end);
			writeLabel(handler);
			writeString(type);
		}

		@Override
		public void visitTypeInsn(int opcode, String type) {
			try {
				mBytes.writeInt(opcode);
				writeString(type);
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public void visitVarInsn(int opcode, int var) {
			try {
				mBytes.writeInt(opcode);
				mBytes.writeInt(var);
			} catch (IOException ex) {
				// never
			}
		}
	}

	private static final class CleanField extends FieldVisitor {
		/** Stream for resulting bytes */
		private DataOutputStream mBytes;

		/** Annotation cleaner */
		private CleanAnnotation mCleanAnnotation;

		/**
		 * Constructor.
		 *
		 * @param dos
		 *            Stream for resulting bytes.
		 * @param cleanAnnotation
		 *            Annotation cleaner.
		 */
		public CleanField(DataOutputStream dos,
				CleanAnnotation cleanAnnotation) {
			super(ASM_API_VERSION);
			this.mBytes = dos;
			this.mCleanAnnotation = cleanAnnotation;
		}

		private void writeString(String s) {
			if (s != null) {
				try {
					mBytes.writeUTF(s);
				} catch (IOException ex) {
					// never
				}
			}
		}

		@Override
		public AnnotationVisitor visitAnnotation(String desc, boolean visible) {
			writeString(desc);
			// Ignore if annotation is not visible.
			return visible ? mCleanAnnotation : null;
		}

		// Ignore non standard attributes.
		// public void visitAttribute(Attribute attr)

		// Nothing to do at the end of the visit.
		// public void visitEnd()
	}

	public static final class CleanAnnotation extends AnnotationVisitor {
		/** Stream for the resulting bytes */
		private DataOutputStream mBytes;

		/**
		 * Constructor.
		 *
		 * @param dos
		 *            Stream for the resulting bytes.
		 */
		public CleanAnnotation(DataOutputStream dos) {
			super(ASM_API_VERSION);
			this.mBytes = dos;
		}

		private void writeString(String s) {
			if (s != null) {
				try {
					mBytes.writeUTF(s);
				} catch (IOException ex) {
					// never
				}
			}
		}

		@Override
		public void visit(String name, Object value) {
			try {
				writeString(name);
				if (value instanceof Byte) {
					mBytes.writeByte((Byte) value);
				} else if (value instanceof Boolean) {
					mBytes.writeBoolean((Boolean) value);
				} else if (value instanceof Character) {
					mBytes.writeChar((Character) value);
				} else if (value instanceof Short) {
					mBytes.writeShort((Short) value);
				} else if (value instanceof Integer) {
					mBytes.writeInt((Integer) value);
				} else if (value instanceof Long) {
					mBytes.writeLong((Long) value);
				} else if (value instanceof Float) {
					mBytes.writeFloat((Float) value);
				} else if (value instanceof Double) {
					mBytes.writeDouble((Double) value);
				} else if (value instanceof String) {
					writeString((String) value);
				} else if (value instanceof Type) {
					writeString(((Type) value).toString());
				}
			} catch (IOException ex) {
				// never
			}
		}

		@Override
		public AnnotationVisitor visitAnnotation(String name, String desc) {
			writeString(name);
			writeString(desc);
			return this;
		}

		@Override
		public AnnotationVisitor visitArray(String name) {
			writeString(name);
			return this;
		}

		// Nothing to do at the end of the visit.
		// public void visitEnd()

		@Override
		public void visitEnum(String name, String desc, String value) {
			writeString(name);
			writeString(desc);
			writeString(value);
		}
	}

	/**
	 * Removes some debug info from the given class file. If the file is not
	 * java class file, the given byte array is returned without any change.
	 *
	 * @param bytes
	 *            Bytes that are from a classfile.
	 * @return classfile without debug info or the given array if the given
	 *         array is not java classfile.
	 */
	public static byte[] removeDebugInfo(byte[] bytes) {
		if (bytes.length >= 4) {
			// Check magic number.
			int magic = ((bytes[0] & 0xff) << 24) | ((bytes[1] & 0xff) << 16)
					| ((bytes[2] & 0xff) << 8) | (bytes[3] & 0xff);
			if (magic != 0xCAFEBABE)
				return bytes;
		} else {
			return bytes;
		}

		// We set the initial size as it cannot exceed that value (but note that
		// this may not be the final size).
		ByteArrayOutputStream baos = new ByteArrayOutputStream(bytes.length);
		DataOutputStream dos = new DataOutputStream(baos);

		try {
			ClassReader classReader = new ClassReader(bytes);
			CleanClass cleanClass = new CleanClass(dos);
			// NOTE: cannot skip debug as code coverage analysis requires line
			// number tables
			// classReader.accept(cleanClass, ClassReader.SKIP_DEBUG);
			classReader.accept(cleanClass, 0);
			if (cleanClass.isFiltered()) {
				return FILTERED_BYTECODE;
			}
		} catch (Exception ex) {
			return bytes;
		}

		return baos.toByteArray();
	}

	public static void main(String... args) throws IOException {
		String inputFileName = args[0];
		String outputFileName = args[1];

		byte[] bytes = FileUtil.readFile(new File(inputFileName));
		byte[] newBytes = removeDebugInfo(bytes);

		DataOutputStream dos = new DataOutputStream(
				new FileOutputStream(outputFileName));
		dos.write(newBytes, 0, newBytes.length);
		dos.close();
	}
}
