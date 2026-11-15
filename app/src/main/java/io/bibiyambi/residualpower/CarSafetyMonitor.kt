package io.bibiyambi.residualpower

import android.car.Car
import android.car.drivingstate.CarUxRestrictions
import android.car.drivingstate.CarUxRestrictionsManager
import android.content.Context
import android.content.ComponentName
import android.content.ServiceConnection
import android.os.Handler
import android.os.IBinder
import android.os.Looper

/** Restriction listener, not parking proof. Service loss immediately revokes UX permission. */
class CarSafetyMonitor(private val context: Context, private val update: (Boolean) -> Unit) {
    private var car: Car? = null
    private var manager: CarUxRestrictionsManager? = null
    private var generation = 0L
    private fun accept(value: CarUxRestrictions) = update(
        !value.isRequiresDistractionOptimization && value.activeRestrictions == CarUxRestrictions.UX_RESTRICTIONS_BASELINE
    )
    @Suppress("DEPRECATION") // Async ServiceConnection overload supports minSdk 28.
    fun start() {
        val token = ++generation
        update(false)
        try {
            car = Car.createCar(context, object : ServiceConnection {
                override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
                    if (token != generation) return
                    try {
                        manager = car?.getCarManager(Car.CAR_UX_RESTRICTION_SERVICE) as? CarUxRestrictionsManager
                        manager?.registerListener { if (token == generation) accept(it) }
                        manager?.currentCarUxRestrictions?.let(::accept) ?: update(false)
                    } catch (_: Exception) { update(false) }
                }
                override fun onServiceDisconnected(name: ComponentName?) {
                    if (token == generation) { manager = null; update(false) }
                }
            }, Handler(Looper.getMainLooper()))
            car?.connect()
        } catch (_: Exception) { update(false) }
    }
    fun stop() {
        generation++
        update(false)
        try { manager?.unregisterListener() } catch (_: Exception) { }
        manager = null; car?.disconnect(); car = null
    }
}
