package io.bibiyambi.residualpower

import org.junit.Assert.*
import org.junit.Test

class NativeRulesTest {
    private fun openedRoof(): GameEngine = GameEngine().apply {
        start(); setSeat(100); collectTool(); openCover(); insertTool(); rotate(-90); rotate(180); openRoof()
    }
    @Test fun `escape requires persistent P05 input but not optional clue reading`() {
        val game = openedRoof()
        game.escape(); assertFalse(game.has(Flag.ACT1_COMPLETE))
        game.completeInput(InputPuzzle.P05); game.escape()
        assertTrue(game.has(Flag.ACT1_COMPLETE)); assertFalse(game.has(Flag.GLASS_READ))
    }
    @Test fun `P05 alone never opens the roof`() {
        val game = GameEngine(); game.completeInput(InputPuzzle.P05); game.escape()
        assertFalse(game.has(Flag.ACT1_COMPLETE))
    }
    @Test fun `bag and glove may be collected in either order and only once`() {
        for (bagFirst in listOf(true, false)) {
            val g = GameEngine()
            val bag = { g.moveCoat(); g.releaseStrap(); g.moveBag(); g.lootBag() }
            val glove = { g.openGlove(); g.lootGlove(); g.readRecord() }
            if (bagFirst) { bag(); glove() } else { glove(); bag() }
            g.combine(Item.CARD, Item.READER); g.lootBag(); g.lootGlove()
            assertTrue(g.has(Item.USB)); assertFalse(g.has(Item.CARD)); assertFalse(g.has(Item.READER))
            g.connectUsb(); assertTrue(g.has(Flag.USB_CONNECTED))
        }
    }
    @Test fun `bag cannot be looted before the game strap is released`() {
        val g = GameEngine(); g.lootBag(); g.moveBag(); g.releaseStrap()
        assertTrue(g.state.inventory.isEmpty()); assertFalse(g.has(Flag.BAG_MOVED))
    }
    @Test fun `native manual folds require both items and the correct order`() {
        val g = GameEngine(); g.fold(true); assertFalse(g.has(Item.FOLDED_MANUAL))
        g.moveCoat(); g.releaseStrap(); g.moveBag(); g.lootBag(); g.openGlove(); g.lootGlove()
        g.combine(Item.MANUAL_A, Item.MANUAL_B); g.inspectVisor()
        g.fold(false); assertFalse(g.has(Item.FOLDED_MANUAL))
        g.fold(true); g.fold(false); assertTrue(g.has(Item.FOLDED_MANUAL))
    }
    @Test fun `tool and socket allow reasoning before optional notes`() {
        val g = openedRoof(); assertTrue(g.has(Flag.ROOF_OPEN)); assertFalse(g.has(Item.FOLDED_MANUAL))
    }
    @Test fun `wrong rotation resets only unfinished sequence`() {
        val g = GameEngine(); g.setSeat(100); g.collectTool(); g.openCover(); g.insertTool()
        g.rotate(-90); g.rotate(-90); g.rotate(180); assertFalse(g.has(Flag.ROOF_UNLOCKED))
        g.rotate(-90); g.rotate(180); assertTrue(g.has(Flag.ROOF_UNLOCKED)); assertTrue(g.has(Item.TOOL))
    }
    @Test fun `mirror needs both restored fog and alignment`() {
        val g = GameEngine(); g.setMirror(14); assertFalse(g.has(Flag.GLASS_READ))
        g.completeInput(InputPuzzle.P05); assertTrue(g.has(Flag.GLASS_READ))
    }
    @Test fun `native save round trip preserves earned progress`() {
        val g = openedRoof(); g.completeInput(InputPuzzle.P05); g.escape()
        val restored = GameEngine(SaveCodec.decode(SaveCodec.encode(g.state)))
        assertEquals(g.state, restored.state)
    }
    @Test fun `foreign schema malformed values and oversized saves are rejected`() {
        for (text in listOf("{}bad", "{\"schemaVersion\":99}", "{\"seat\":101}", " ".repeat(65537), "{\"parked\":true}")) {
            assertThrows(IllegalArgumentException::class.java) { SaveCodec.decode(text) }
        }
    }
    @Test fun `saved state never contains transient authorization or partial input`() {
        val text = SaveCodec.encode(openedRoof().state)
        for (name in listOf("parked", "connected", "permission", "epoch", "pending")) assertFalse(text.contains(name))
    }
}
