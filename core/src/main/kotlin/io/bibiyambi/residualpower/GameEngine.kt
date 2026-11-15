package io.bibiyambi.residualpower

import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

@Serializable enum class Scene(val title: String) {
    S01("전면 운전석"), S02("조수석"), S03("뒷좌석"), S04("룸미러·오디오"),
    S05("운전석 하단"), S06("천장")
}
@Serializable enum class Item(val label: String, val asset: String) {
    PHOTO("훼손 사진", "photo"), MANUAL_A("안내서 A", "manualA"), MANUAL_B("안내서 B", "manualB"),
    CARD("메모리 카드", "card"), READER("카드 리더기", "reader"), USB("카드+리더기", "usb"),
    MANUAL("맞춘 안내서", "manualJoined"), FOLD_NOTE("접기 표시", "foldNote"),
    FOLDED_MANUAL("접은 도면", "manualFolded"), TOOL("삼각 수동 도구", "tool")
}
@Serializable enum class Flag {
    STARTED, WIPER_OBSERVED, COAT_MOVED, STRAP_RELEASED, BAG_MOVED, BAG_LOOTED,
    GLOVE_OPEN, GLOVE_LOOTED, RECORD_READ, USB_CONNECTED, LEFT_HEARD, RIGHT_HEARD,
    FOG_RESTORED, GLASS_READ, TOOL_FOUND, FOLD_NOTE_FOUND, COVER_OPEN, TOOL_INSERTED,
    ROOF_UNLOCKED, ROOF_OPEN, ACT1_COMPLETE
}
@Serializable data class GameState(
    val format: String = "residual-native-v1",
    val schemaVersion: Int = 1,
    val scene: Scene = Scene.S01,
    val flags: Set<Flag> = emptySet(),
    val inventory: Set<Item> = emptySet(),
    val clues: Set<String> = emptySet(),
    val seat: Int = 50,
    val mirror: Int = -20
)

/** Native rules. Vehicle authorization and unfinished input are deliberately not persisted. */
class GameEngine(saved: GameState = GameState()) {
    var state: GameState = SaveCodec.validate(saved)
        private set
    private var foldStep = 0
    private var rotationStep = 0
    fun has(flag: Flag) = flag in state.flags
    fun has(item: Item) = item in state.inventory
    private fun mark(vararg flags: Flag) { state = state.copy(flags = state.flags + flags) }
    private fun add(vararg items: Item) { state = state.copy(inventory = state.inventory + items) }
    private fun note(vararg ids: String) { state = state.copy(clues = state.clues + ids) }
    fun start() { mark(Flag.STARTED) }
    fun move(scene: Scene) { state = state.copy(scene = scene); interrupt() }
    fun interrupt() { foldStep = 0; rotationStep = 0 }
    fun completeInput(puzzle: InputPuzzle) {
        when (puzzle) {
            InputPuzzle.P01 -> { mark(Flag.WIPER_OBSERVED); note("frameRain") }
            InputPuzzle.P05 -> { mark(Flag.FOG_RESTORED); readGlass() }
        }
    }
    fun inspectFrame(): String { note("frame"); return "프레임 04. 옆문은 막혀 있고 위쪽에만 여유가 있다." }
    fun moveCoat(): String { mark(Flag.COAT_MOVED); return "외투 아래에 가방 고정 끈이 보인다." }
    fun releaseStrap(): String {
        if (!has(Flag.COAT_MOVED)) return "가방 위 외투를 먼저 조사하자."
        mark(Flag.STRAP_RELEASED); note("occupancy"); return "게임 속 가방 고정 끈을 풀었다."
    }
    fun moveBag(): String {
        if (!has(Flag.STRAP_RELEASED)) return "가방 고정 끈이 걸려 있다."
        mark(Flag.BAG_MOVED); return "가방을 바닥으로 옮겼다. 내용물을 확인할 수 있다."
    }
    fun lootBag(): String {
        if (!has(Flag.BAG_MOVED)) return "가방을 먼저 옮겨야 한다."
        if (has(Flag.BAG_LOOTED)) return "내용물은 모두 챙겼다."
        mark(Flag.BAG_LOOTED); add(Item.PHOTO, Item.MANUAL_A, Item.CARD); note("photo")
        return "훼손 사진, 안내서 A, 메모리 카드를 얻었다."
    }
    fun openGlove(): String { mark(Flag.GLOVE_OPEN); return "잠겨 있지 않은 서랍을 열었다." }
    fun lootGlove(): String {
        if (!has(Flag.GLOVE_OPEN)) return "서랍이 닫혀 있다."
        if (has(Flag.GLOVE_LOOTED)) return "서랍의 물건은 모두 챙겼다."
        mark(Flag.GLOVE_LOOTED); add(Item.READER, Item.MANUAL_B)
        return "카드 리더기와 안내서 B를 얻었다."
    }
    fun readRecord(): String {
        if (!has(Flag.GLOVE_OPEN)) return "서랍 안쪽을 확인하자."
        mark(Flag.RECORD_READ); note("record"); return "M-04 / 최종 운행 02:17 / 회수 예정 03:40 / 상태 보류."
    }
    fun combine(first: Item, second: Item): String {
        if (!has(first) || !has(second) || first == second) return "소지품 두 개를 선택하자."
        val pair = setOf(first, second)
        val result = when (pair) {
            setOf(Item.CARD, Item.READER) -> Item.USB
            setOf(Item.MANUAL_A, Item.MANUAL_B) -> Item.MANUAL
            else -> return "두 물건은 맞물리지 않는다."
        }
        state = state.copy(inventory = state.inventory - pair + result)
        return "${result.label}를 만들었다."
    }
    fun connectUsb(): String {
        if (!has(Item.USB)) return "카드와 리더기를 조합해야 한다."
        mark(Flag.USB_CONNECTED); note("voices"); return "손상된 녹음을 인식했다. 좌우 채널을 확인할 수 있다."
    }
    fun hearChannel(left: Boolean): String {
        if (!has(Flag.USB_CONNECTED)) return "USB 입력을 먼저 연결하자."
        mark(if (left) Flag.LEFT_HEARD else Flag.RIGHT_HEARD)
        note(if (left) "voiceLeft" else "voiceRight")
        return if (left) "흔적은 지워도 남아." else "끝까지 밀어. 그 아래."
    }
    fun setMirror(value: Int): String {
        state = state.copy(mirror = value.coerceIn(-30, 30)); readGlass()
        return if (has(Flag.GLASS_READ)) "유리의 문장과 레일 그림을 수첩에 기록했다." else "게임 룸미러의 각도가 바뀌었다."
    }
    private fun readGlass() {
        if (has(Flag.FOG_RESTORED) && kotlin.math.abs(state.mirror - 14) <= 4) {
            mark(Flag.GLASS_READ); note("glass")
        }
    }
    fun setSeat(value: Int): String {
        state = state.copy(seat = value.coerceIn(0, 100))
        return if (state.seat == 100) "레일 끝에 닿았다. 아래 공간을 조사하자." else "게임 시트의 위치가 바뀌었다."
    }
    fun collectTool(): String {
        if (state.seat < 99) return "레일 아래 공간이 좁다."
        if (has(Flag.TOOL_FOUND)) return "도구는 이미 챙겼다."
        mark(Flag.TOOL_FOUND); add(Item.TOOL); note("tool"); return "삼각 수동 도구를 얻었다."
    }
    fun inspectVisor(): String {
        if (!has(Flag.FOLD_NOTE_FOUND)) { mark(Flag.FOLD_NOTE_FOUND); add(Item.FOLD_NOTE); note("fold") }
        return "안내서 왼쪽 1/3을 가운데로, 아래 1/3을 위로."
    }
    fun fold(left: Boolean): String {
        if (!has(Item.MANUAL) || !has(Item.FOLD_NOTE)) return "맞춘 안내서와 접기 표시가 필요하다."
        if (left != (foldStep == 0)) { foldStep = 0; return "기호가 이어지지 않아 다시 펼쳤다." }
        foldStep++
        if (foldStep < 2) return "첫 점선을 접었다."
        state = state.copy(inventory = state.inventory - Item.MANUAL + Item.FOLDED_MANUAL)
        note("manual"); foldStep = 0
        return "삼각 소켓 · 반시계 90° · 시계 180°. 도형이 이어졌다."
    }
    fun openCover(): String { mark(Flag.COVER_OPEN); return "커버 안에 삼각 소켓이 드러났다." }
    fun insertTool(): String {
        if (!has(Flag.COVER_OPEN) || !has(Item.TOOL)) return "열린 커버와 삼각 도구가 필요하다."
        mark(Flag.TOOL_INSERTED); rotationStep = 0; return "도구가 소켓에 맞물렸다."
    }
    fun rotate(angle: Int): String {
        if (!has(Flag.TOOL_INSERTED)) return "먼저 도구를 끼워야 한다."
        if (has(Flag.ROOF_UNLOCKED)) return "잠금은 이미 풀렸다."
        val expected = if (rotationStep == 0) -90 else 180
        if (angle != expected) { rotationStep = 0; return "방향이 맞지 않는다. 첫 순서로 돌아갔다." }
        rotationStep++
        if (rotationStep == 1) return "첫 잠금쇠가 움직였다."
        mark(Flag.ROOF_UNLOCKED); note("roof"); return "수동 잠금이 해제됐다."
    }
    fun openRoof(): String {
        if (!has(Flag.ROOF_UNLOCKED)) return "수동 장치가 잠겨 있다."
        mark(Flag.ROOF_OPEN); return "게임 선루프가 열렸다."
    }
    fun escape(): String {
        if (!has(Flag.ROOF_OPEN)) return "위쪽 통로가 아직 닫혀 있다."
        // Persistent input result, independent from reading the optional clue.
        if (!has(Flag.FOG_RESTORED)) return "유리 흔적 판독부의 풍량 입력을 복원해야 탈출 경로를 확인할 수 있다."
        mark(Flag.ACT1_COMPLETE); return "차 밖으로 나왔다. 감시실의 전원이 살아 있다."
    }
}

object SaveCodec {
    private val json = Json { encodeDefaults = true }
    fun validate(state: GameState): GameState {
        require(state.format == "residual-native-v1" && state.schemaVersion == 1)
        require(state.seat in 0..100 && state.mirror in -30..30)
        require(state.clues.size <= 64 && state.clues.all { it.matches(Regex("[A-Za-z]{1,40}")) })
        return state
    }
    fun encode(state: GameState) = json.encodeToString(validate(state))
    fun decode(text: String): GameState {
        require(text.toByteArray().size <= 64 * 1024)
        return validate(json.decodeFromString<GameState>(text))
    }
}
