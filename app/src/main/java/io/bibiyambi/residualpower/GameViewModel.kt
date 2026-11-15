package io.bibiyambi.residualpower

import android.app.Application
import android.os.SystemClock
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import org.json.JSONObject

class GameViewModel(application: Application) : AndroidViewModel(application) {
    private val saves = SaveRepository(application.filesDir)
    private var engine = GameEngine(saves.load())
    var state by mutableStateOf(engine.state)
        private set
    var message by mutableStateOf(saves.notice)
        private set
    var paused by mutableStateOf(true)
        private set
    var allowed by mutableStateOf(false)
        private set
    var simulatedParking by mutableStateOf(false)
        private set
    var inputStatus by mutableStateOf("단말을 활성화한 뒤 입력하세요.")
        private set
    var sdkStatus by mutableStateOf("SDK 연결 전")
    var panel by mutableStateOf<String?>(null)
    var selectedItems by mutableStateOf<Set<Item>>(emptySet())
    var saveWarning by mutableStateOf(saves.notice)
        private set
    val gate = SafetyGate()
    private val notes = JSONObject(application.assets.open("notes.json").bufferedReader().use { it.readText() })
    private val audio = NativeAudio(application) { pause("오디오 포커스를 잃었습니다. 직접 재개해 주세요.") }
    private val input = InputSession { puzzle ->
        engine.completeInput(puzzle); inputStatus = "입력 복원 완료 · 드러난 단서를 조사하세요."
        publish("입력이 복원됐습니다. 드러난 흔적을 조사하세요.")
    }
    init {
        viewModelScope.launch {
            while (isActive) {
                val now = SystemClock.elapsedRealtime()
                if (BuildConfig.SIMULATED_PARKING && simulatedParking && gate.foreground && gate.focused) {
                    // Explicit development-only simulation; never repackages a vehicle value.
                    gate.observeParking(true, now)
                }
                allowed = gate.allowed(now)
                if (!allowed && !paused) pause("정차·화면 상태가 바뀌어 진행을 멈췄습니다.")
                if (!paused) {
                    input.tick(now, allowed)
                    input.context?.let { inputStatus = "${it.puzzle.name} · ${it.step}/${it.puzzle.sequence.size} 확인 · 각 상태 0.7초 유지" }
                }
                delay(100)
            }
        }
    }
    private fun persist() {
        if (saves.locked) return
        try { saves.save(engine.state); saveWarning = "" } catch (_: Exception) {
            saveWarning = "저장하지 못했습니다. 앱을 닫기 전에 다시 시도하세요."
        }
    }
    private fun publish(feedback: String = "") {
        state = engine.state
        selectedItems = selectedItems.intersect(state.inventory)
        if (feedback.isNotBlank()) message = feedback
        persist()
    }
    fun act(action: GameEngine.() -> String) {
        if (paused || !gate.allowed(SystemClock.elapsedRealtime())) return
        publish(engine.action())
    }
    fun move(scene: Scene) {
        if (paused || !gate.allowed(SystemClock.elapsedRealtime())) return
        input.clear(); engine.move(scene); panel = null; publish()
    }
    fun simulateParking(parked: Boolean) {
        if (!BuildConfig.SIMULATED_PARKING) return
        simulatedParking = parked
        if (!parked) { gate.invalidate(); allowed = false; pause("개발용 가상 정차를 해제했습니다.") }
    }
    fun foreground(value: Boolean) {
        gate.foreground = value
        if (!value) { gate.invalidate(); allowed = false; pause("앱이 백그라운드로 이동했습니다.") }
    }
    fun focus(value: Boolean) {
        gate.focused = value
        if (!value) { gate.invalidate(); allowed = false; pause("화면이 가려져 진행을 멈췄습니다.") }
    }
    fun ux(value: Boolean) {
        gate.uxAllowed = value
        if (!value) { allowed = false; pause("플랫폼 주행 제한이 적용됐습니다.") }
    }
    fun resume() {
        if (!gate.allowed(SystemClock.elapsedRealtime())) return
        input.clear(); paused = false; engine.start(); publish("차 안에 남은 흔적을 조사하세요.")
    }
    fun pause(reason: String = "일시정지했습니다.") {
        input.clear(); engine.interrupt(); audio.stop(); paused = true; panel = null
        inputStatus = "중단된 입력은 새로 활성화해야 합니다."; publish(reason)
    }
    fun arm(puzzle: InputPuzzle) {
        if (paused || !gate.allowed(SystemClock.elapsedRealtime())) return
        input.arm(puzzle, SystemClock.elapsedRealtime())
        inputStatus = "${puzzle.name} 활성 · 새 상태를 기다립니다."
    }
    fun simulationValue(signal: String, value: String) {
        if (paused || !BuildConfig.SIMULATED_PARKING) return
        val ctx = input.context ?: return
        if (ctx.puzzle.signal != signal) return
        val now = SystemClock.elapsedRealtime()
        input.receive(InputPacket(ctx, InputSource.SIMULATION, value, now), now, gate.allowed(now))
    }
    fun combine() {
        if (selectedItems.size == 2) {
            val pair = selectedItems.toList(); act { combine(pair[0], pair[1]) }; selectedItems = emptySet()
        }
    }
    fun select(item: Item) { selectedItems = if (item in selectedItems) selectedItems - item else (selectedItems + item).toList().takeLast(2).toSet() }
    fun clue(id: String): Pair<String, String> {
        val note = notes.optJSONArray(id)
        return (note?.optString(0) ?: id) to (note?.optString(1) ?: "")
    }
    fun play(left: Boolean) {
        if (paused || !gate.allowed(SystemClock.elapsedRealtime()) || !engine.has(Flag.USB_CONNECTED)) return
        if (!audio.playChannel(left) { act { hearChannel(left) } }) message = "오디오를 재생할 수 없습니다. 자막을 이용하세요."
    }
    fun stopAudio() = audio.stop()
    fun closePanel() { audio.stop(); input.clear(); panel = null }
    fun recover() {
        try { saves.authorizeReplacement(); persist(); saveWarning = "" }
        catch (_: Exception) { saveWarning = "원본 보존에 실패했습니다. 복구를 중단했습니다." }
    }
    fun newGame() {
        pause()
        try {
            saves.authorizeReplacement(); engine = GameEngine(); state = engine.state
            selectedItems = emptySet(); saveWarning = ""; publish("새 기록을 만들었습니다. 직접 시작해 주세요.")
        } catch (_: Exception) { saveWarning = "기존 기록 보존에 실패했습니다. 새 게임을 만들지 않았습니다." }
    }
    override fun onCleared() { audio.stop(); super.onCleared() }
}
