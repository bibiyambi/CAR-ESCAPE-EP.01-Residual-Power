package io.bibiyambi.residualpower

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.media.MediaPlayer

class NativeAudio(private val context: Context, private val interrupted: () -> Unit) {
    private val manager = context.getSystemService(AudioManager::class.java)
    private var player: MediaPlayer? = null
    private var generation = 0L
    private val attributes = AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME)
        .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build()
    private val focus = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
        .setAudioAttributes(attributes).setOnAudioFocusChangeListener { change ->
            if (change != AudioManager.AUDIOFOCUS_GAIN) { stop(); interrupted() }
        }.build()
    fun playChannel(left: Boolean, complete: () -> Unit): Boolean {
        stop()
        if (manager.requestAudioFocus(focus) != AudioManager.AUDIOFOCUS_REQUEST_GRANTED) return false
        val token = ++generation
        return try {
            val media = MediaPlayer()
            player = media
            media.setAudioAttributes(attributes)
            context.assets.openFd("assets/audio/stereo-recording.wav").use {
                media.setDataSource(it.fileDescriptor, it.startOffset, it.length)
            }
            media.setVolume(if (left) 1f else 0f, if (left) 0f else 1f)
            media.setOnCompletionListener { if (generation == token) { stop(); complete() } }
            media.setOnErrorListener { _, _, _ -> stop(); interrupted(); true }
            media.prepare(); media.start(); true
        } catch (_: Exception) { stop(); false }
    }
    fun stop() {
        generation++
        player?.release(); player = null
        manager.abandonAudioFocusRequest(focus)
    }
}
