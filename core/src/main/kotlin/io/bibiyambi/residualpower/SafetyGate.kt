package io.bibiyambi.residualpower

/** UX permission alone never creates parked evidence. No authorization is restored from a save. */
class SafetyGate {
    var foreground = false
    var focused = false
    var uxAllowed = false
    private var parked = false
    private var observedAt = -1L
    fun observeParking(allowed: Boolean, now: Long) { parked = allowed; observedAt = now }
    fun invalidate() { parked = false; observedAt = -1 }
    fun allowed(now: Long): Boolean = foreground && focused && uxAllowed && parked &&
        observedAt >= 0 && now >= observedAt && now - observedAt <= 2000
}
