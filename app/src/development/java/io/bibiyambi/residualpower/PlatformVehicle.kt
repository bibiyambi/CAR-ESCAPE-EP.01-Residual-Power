package io.bibiyambi.residualpower

import android.content.Context

/** Clearly separate from the Pleos flavor: no claim of SDK or vehicle connectivity. */
class PlatformVehicle(context: Context) {
    fun start(status: (String) -> Unit) = status("개발 빌드 · SDK 미연결 · 화면 모의 입력 전용")
    fun stop() = Unit
    fun close() = Unit
}
