package io.bibiyambi.residualpower

import org.junit.Assert.*
import org.junit.Test

class InputSafetyTest {
    @Test fun `700ms holds and distinct wiper transitions are required`() {
        val done = mutableListOf<InputPuzzle>(); val i = InputSession { done += it }
        i.arm(InputPuzzle.P01, 10000)
        fun send(value: String, time: Long) = i.receive(InputPacket(i.context!!, InputSource.SIMULATION, value, time), time, true)
        send("OFF", 10001); assertFalse(i.tick(10700, true)); assertFalse(i.tick(10701, true))
        assertEquals(1, i.context!!.step)
        send("OFF", 10800); i.tick(11500, true); assertTrue(done.isEmpty())
        send("ACTIVE", 11600); assertTrue(i.tick(12300, true)); assertEquals(listOf(InputPuzzle.P01), done)
    }
    @Test fun `short excursion back to the last value cancels candidate`() {
        val i = InputSession { fail("premature completion") }; i.arm(InputPuzzle.P01, 10000)
        fun send(v: String, t: Long) = i.receive(InputPacket(i.context!!, InputSource.SIMULATION, v, t), t, true)
        send("OFF", 10001); i.tick(10701, true)
        send("ACTIVE", 10800); send("OFF", 11000); i.tick(11500, true)
        assertEquals(1, i.context!!.step)
    }
    @Test fun `old context wrong source and future stale or duplicate events are discarded`() {
        val i = InputSession { fail() }; i.arm(InputPuzzle.P01, 10000)
        val old = i.context!!; i.arm(InputPuzzle.P05, 10001)
        assertFalse(i.receive(InputPacket(old, InputSource.SIMULATION, "LOW", 10002), 10002, true))
        val c = i.context!!
        for (p in listOf(InputPacket(c, InputSource.VEHICLE, "LOW", 10002), InputPacket(c, InputSource.SIMULATION, "LOW", 9999), InputPacket(c, InputSource.SIMULATION, "LOW", 20000))) {
            assertFalse(i.receive(p, 10002, true))
        }
    }
    @Test fun `unknown raw signal revokes an unfinished hold`() {
        val i = InputSession { fail() }; i.arm(InputPuzzle.P05, 10000); val c = i.context!!
        i.receive(InputPacket(c, InputSource.SIMULATION, "LOW", 10001), 10001, true)
        i.receive(InputPacket(c, InputSource.SIMULATION, null, 10002), 10002, true)
        assertFalse(i.tick(10701, true))
    }
    @Test fun `pause and safety loss invalidate old callbacks`() {
        val i = InputSession { fail() }; i.arm(InputPuzzle.P05, 10000); val c = i.context!!
        i.receive(InputPacket(c, InputSource.SIMULATION, "LOW", 10001), 10001, true)
        i.tick(10701, false); i.arm(InputPuzzle.P05, 11000)
        assertFalse(i.receive(InputPacket(c, InputSource.SIMULATION, "LOW", 11001), 11001, true))
    }
    @Test fun `unverified OFF mode never changes source or progress`() {
        val i = InputSession {}; i.arm(InputPuzzle.P05, 10000)
        assertFalse(i.switchSource(InputSource.VEHICLE, false)); assertNotNull(i.context)
        assertEquals(InputSource.SIMULATION, i.source)
    }
    @Test fun `clock reversal invalidates a pending hold`() {
        val i = InputSession { fail() }; i.arm(InputPuzzle.P05, 10000)
        i.receive(InputPacket(i.context!!, InputSource.SIMULATION, "LOW", 10001), 10001, true)
        assertFalse(i.tick(9999, true)); assertNull(i.context)
    }
    @Test fun `UX flags alone never establish parked evidence`() {
        val g = SafetyGate(); g.foreground = true; g.focused = true; g.uxAllowed = true
        assertFalse(g.allowed(10000)); g.observeParking(true, 10000); assertTrue(g.allowed(10001))
    }
    @Test fun `expired evidence background obscuring restriction and reversal block`() {
        val g = SafetyGate(); g.foreground = true; g.focused = true; g.uxAllowed = true
        g.observeParking(true, 10000)
        assertFalse(g.allowed(9999)); assertFalse(g.allowed(12001))
        g.focused = false; assertFalse(g.allowed(10001)); g.focused = true
        g.foreground = false; assertFalse(g.allowed(10001)); g.foreground = true
        g.uxAllowed = false; assertFalse(g.allowed(10001))
    }
}
