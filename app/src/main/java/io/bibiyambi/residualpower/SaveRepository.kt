package io.bibiyambi.residualpower

import android.util.AtomicFile
import java.io.File
import java.security.MessageDigest

/** App-private atomic JSON with checksum and one previous valid save. */
class SaveRepository(private val directory: File) {
    private val current = AtomicFile(File(directory, "native-save.json"))
    private val previous = AtomicFile(File(directory, "native-save.previous.json"))
    private fun exists(file: AtomicFile) = file.baseFile.exists() || File(file.baseFile.path + ".bak").exists()
    var locked = false
        private set
    var notice = ""
        private set
    private fun digest(text: String) = MessageDigest.getInstance("SHA-256")
        .digest(text.toByteArray()).joinToString("") { "%02x".format(it) }
    private fun read(file: AtomicFile): GameState {
        require(file.baseFile.length() <= 70 * 1024)
        val body = file.openRead().bufferedReader().use { it.readText() }
        val parts = body.split('\n', limit = 2)
        require(parts.size == 2 && digest(parts[1]) == parts[0])
        return SaveCodec.decode(parts[1])
    }
    fun load(): GameState {
        if (!exists(current)) return GameState()
        return try { read(current) } catch (_: Exception) {
            locked = true
            try {
                val backup = read(previous)
                notice = "저장 손상을 감지했습니다. 이전 정상본을 표시합니다. ‘백업 복구’를 눌러 저장을 재개하세요."
                backup
            } catch (_: Exception) {
                notice = "저장 기록을 읽지 못했습니다. 원본을 보존했습니다. 새 게임을 선택하면 새 기록을 만듭니다."
                GameState()
            }
        }
    }
    private fun write(file: AtomicFile, state: GameState) {
        val text = SaveCodec.encode(state)
        val stream = file.startWrite()
        try {
            stream.write((digest(text) + "\n" + text).toByteArray())
            file.finishWrite(stream)
        } catch (e: Exception) { file.failWrite(stream); throw e }
    }
    fun save(state: GameState) {
        check(!locked)
        if (exists(current)) write(previous, read(current))
        write(current, state)
    }
    fun authorizeReplacement() {
        // Explicit recovery/new-game action preserves unreadable bytes before replacing.
        if (exists(current)) {
            val archive = File(directory, "native-save.preserved.${System.currentTimeMillis()}.json")
            current.openRead().use { input -> archive.outputStream().use { input.copyTo(it) } }
        }
        current.delete(); locked = false; notice = ""
    }
}
