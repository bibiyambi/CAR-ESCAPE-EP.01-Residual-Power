package io.bibiyambi.residualpower

enum class InputPuzzle(val signal: String, val sequence: List<String>) {
    P01("wiper", listOf("OFF", "ACTIVE")), P05("fan", listOf("LOW"))
}
enum class InputSource { SIMULATION, VEHICLE }
data class InputContext(val epoch: Long, val puzzle: InputPuzzle, val step: Int)
data class InputPacket(val context: InputContext, val source: InputSource, val value: String?, val receivedAt: Long)

/** All times are monotonic milliseconds. SDK requests must capture context before issuing the read. */
class InputSession(private val complete: (InputPuzzle) -> Unit) {
    var context: InputContext? = null
        private set
    var source = InputSource.SIMULATION
        private set
    private var epoch = 0L
    private var armedAt = 0L
    private var lastTimestamp = -1L
    private var stableValue: String? = null
    private var pending: InputPacket? = null
    private var since = 0L
    fun arm(puzzle: InputPuzzle, now: Long) {
        clear(); context = InputContext(epoch, puzzle, 0); armedAt = now
    }
    fun clear() {
        epoch++; context = null; pending = null; stableValue = null; lastTimestamp = -1
    }
    fun switchSource(next: InputSource, verifiedVehicle: Boolean): Boolean {
        if (next == InputSource.VEHICLE && !verifiedVehicle) return false
        clear(); source = next; return true
    }
    fun receive(packet: InputPacket, now: Long, safe: Boolean): Boolean {
        if (!safe) { clear(); return false }
        val ctx = context ?: return false
        if (packet.context != ctx || packet.source != source || packet.receivedAt < armedAt ||
            packet.receivedAt > now || now - packet.receivedAt > 2000 || packet.receivedAt <= lastTimestamp) return false
        lastTimestamp = packet.receivedAt
        val allowed = if (ctx.puzzle.signal == "wiper") setOf("OFF", "ACTIVE") else setOf("LOW", "MID")
        if (packet.value !in allowed) { pending = null; return false }
        if (pending?.value != packet.value) pending = null
        if (packet.value == stableValue) return false
        if (pending == null) { pending = packet; since = now } else pending = packet
        return true
    }
    fun tick(now: Long, safe: Boolean): Boolean {
        if (!safe) { clear(); return false }
        val p = pending ?: return false
        val ctx = context ?: return false
        if (now - p.receivedAt > 2000 || now < since) { clear(); return false }
        if (now - since < 700) return false
        pending = null; stableValue = p.value
        if (p.value != ctx.puzzle.sequence[ctx.step]) {
            context = ctx.copy(step = 0); stableValue = null; return false
        }
        if (ctx.step + 1 == ctx.puzzle.sequence.size) {
            clear(); complete(ctx.puzzle); return true
        }
        context = ctx.copy(step = ctx.step + 1)
        return false
    }
}
