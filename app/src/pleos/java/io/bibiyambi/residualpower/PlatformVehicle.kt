package io.bibiyambi.residualpower

import ai.pleos.playground.vehicle.Vehicle
import android.content.Context
import android.os.Handler
import android.os.Looper
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/** Official typed lifecycle only. No guessed getters, write APIs, credentials, or verified mappings. */
class PlatformVehicle(context: Context) {
    private val vehicle = Vehicle(context.applicationContext)
    private val worker = Executors.newSingleThreadExecutor()
    private val main = Handler(Looper.getMainLooper())
    private val generation = AtomicLong()
    fun start(status: (String) -> Unit) {
        val token = generation.incrementAndGet()
        worker.execute {
            val result = try {
                vehicle.initialize()
                "SDK 초기화 호출 완료 · 실제 연결·capability·V00 검증 대기"
            } catch (_: Exception) { "SDK 초기화 실패 · 실행 차단" }
            main.post { if (token == generation.get()) status(result) }
        }
    }
    fun stop() { generation.incrementAndGet(); worker.execute { try { vehicle.release() } catch (_: Exception) {} } }
    fun close() { stop(); worker.shutdown() }
}
