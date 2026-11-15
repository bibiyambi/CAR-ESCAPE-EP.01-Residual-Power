package io.bibiyambi.residualpower

import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels

class GameActivity : ComponentActivity() {
    private val model: GameViewModel by viewModels()
    private var restrictions: CarSafetyMonitor? = null
    private var vehicle: PlatformVehicle? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (packageManager.hasSystemFeature(PackageManager.FEATURE_AUTOMOTIVE)) {
            restrictions = CarSafetyMonitor(this, model::ux)
        } else model.ux(BuildConfig.SIMULATED_PARKING)
        try { vehicle = PlatformVehicle(this) }
        catch (_: Exception) { model.sdkStatus = "SDK 생성 실패 · 실행 차단" }
        setContent { ResidualApp(model) { finish() } }
    }
    override fun onStart() {
        super.onStart()
        model.foreground(true)
        restrictions?.start()
        vehicle?.start { model.sdkStatus = it }
    }
    override fun onStop() {
        model.foreground(false)
        restrictions?.stop()
        vehicle?.stop()
        super.onStop()
    }
    override fun onWindowFocusChanged(hasFocus: Boolean) { super.onWindowFocusChanged(hasFocus); model.focus(hasFocus) }
    override fun onDestroy() { vehicle?.close(); super.onDestroy() }
}
