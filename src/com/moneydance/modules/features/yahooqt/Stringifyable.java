/************************************************************\
 *      Copyright (C) 2009 Reilly Technologies, L.L.C.      *
 \************************************************************/
package com.moneydance.modules.features.yahooqt;

/**
 * This interface is a marker for classes that enforce the following conditions: <ul> <li>{@link #toString()} is
 * overridden <li>The class has a public static method that takes a single <code>String</code> and returns an instance
 * of the class <li>{@link #hashCode()} and {@link #equals(Object)} are overridden to provide equivalence <li>It is
 * always the case that for an instance <code>a</code> of a <code>Stringifyable</code> class <code>Foo</code>,
 * a.equals(new Foo(a.toString()) returns <code>true</code></ul> Note that while an implementing class may have a
 * constructor that takes a single <code>String</code>, the second point is necessary for cases when an implementor
 * wishes to manage the set of instances rather than always create new instances.
 *
 * @author Jay Detwiler
 */
public interface Stringifyable {
}
