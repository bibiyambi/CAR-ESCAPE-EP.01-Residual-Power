package io.bibiyambi.residualpower

import android.graphics.BitmapFactory
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

private val Ink = Color(0xff101e23)
private val Paper = Color(0xffe9dfce)
private val Gold = Color(0xffcfb684)
private val Teal = Color(0xff8ebbb4)

@Composable fun ResidualApp(model: GameViewModel, exit: () -> Unit) {
    var exitPrompt by remember { mutableStateOf(false) }
    BackHandler {
        if (model.panel != null) model.closePanel()
        else if (!model.paused) model.pause()
        else exitPrompt = true
    }
    MaterialTheme(colorScheme = darkColorScheme(primary = Gold, secondary = Teal, background = Ink, surface = Color(0xff1a2c32), onSurface = Paper)) {
        Surface(Modifier.fillMaxSize(), color = Ink) {
            if (model.paused || !model.allowed) {
                Column(Modifier.safeDrawingPadding().fillMaxSize().verticalScroll(rememberScrollState()).padding(32.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
                    Text("M—04 / NATIVE ANDROID", color = Gold, letterSpacing = 3.sp)
                    Text("잔류 전원", fontSize = 42.sp, fontWeight = FontWeight.Light)
                    Text("RESIDUAL POWER", letterSpacing = 5.sp, color = Teal)
                    Text("열리지 않는 문. 사라진 열쇠.\n이 차에는 내가 잊은 흔적이 남아 있다.", fontSize = 20.sp)
                    HorizontalDivider()
                    Text(if (model.allowed) "정차 확인 · 시작 또는 재개를 기다립니다." else "정차와 화면 상태를 확인하기 전에는 게임을 표시하지 않습니다.")
                    Text(model.sdkStatus, color = Teal)
                    if (BuildConfig.SIMULATED_PARKING) {
                        Text("개발용 시연 · 실제 차량 제어 없음 · 네이티브 1막", color = Gold)
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Switch(checked = model.simulatedParking, onCheckedChange = model::simulateParking)
                            Text("개발용 가상 정차", Modifier.padding(start = 12.dp))
                        }
                    } else Text("Pleos 정차 근거·읽기 capability 검증 대기. 가상 신호로 대체하지 않습니다.")
                    if (model.message.isNotBlank()) Text(model.message)
                    if (model.saveWarning.isNotBlank()) {
                        Text(model.saveWarning, color = Gold)
                        OutlinedButton(onClick = model::recover) { Text("백업 복구 / 저장 재시도") }
                    }
                    Button(onClick = model::resume, enabled = model.allowed) {
                        Text(if (Flag.STARTED in model.state.flags) "직접 재개" else "눈을 뜬다")
                    }
                    OutlinedButton(onClick = { model.panel = "new-confirm" }) { Text("새 게임") }
                    if (model.panel == "new-confirm") {
                        Text("현재 기록을 별도 파일로 보존하고 새 게임을 만듭니다.")
                        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Button(onClick = { model.newGame(); model.panel = null }) { Text("새 기록 만들기") }
                            OutlinedButton(onClick = { model.panel = null }) { Text("취소") }
                        }
                    }
                    if (exitPrompt) {
                        Text("앱을 종료할까요? 마지막 저장 상태는 유지됩니다.")
                        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            Button(onClick = exit) { Text("종료") }
                            OutlinedButton(onClick = { exitPrompt = false }) { Text("돌아가기") }
                        }
                    }
                }
            } else GameScreen(model)
        }
    }
}

@Composable private fun GameScreen(model: GameViewModel) {
    val state = model.state
    Box(Modifier.fillMaxSize().safeDrawingPadding()) {
        Column(Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Text("잔류 전원", fontSize = 26.sp, color = Paper, modifier = Modifier.weight(1f))
                Text("01막 / ${state.scene.name}", color = Gold)
                TextButton(onClick = { model.panel = "notebook" }) { Text("수첩") }
                TextButton(onClick = { model.pause() }) { Text("일시정지") }
            }
            Text("네이티브 개발판 · 가상 정차 · 화면 조작 보조 ON", color = Teal, fontSize = 12.sp)
            Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Scene.entries.forEach { scene ->
                    FilterChip(selected = scene == state.scene, onClick = { model.move(scene) }, label = { Text(scene.title) })
                }
            }
            BoxWithConstraints(Modifier.weight(1f).fillMaxWidth()) {
                if (maxWidth > 840.dp) {
                    Row(Modifier.fillMaxSize(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                        SceneArtwork(state, Modifier.weight(1f).fillMaxHeight())
                        Column(Modifier.width(300.dp).fillMaxHeight().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Investigations(model)
                        }
                    }
                } else {
                    Column(Modifier.fillMaxSize()) {
                        SceneArtwork(state, Modifier.weight(1f).fillMaxWidth())
                        Column(Modifier.heightIn(max = 180.dp).fillMaxWidth().verticalScroll(rememberScrollState())) { Investigations(model) }
                    }
                }
            }
            Text(model.message.ifBlank { "화면 속 물건을 조사하세요." }, color = Paper, minLines = 2)
            if (model.saveWarning.isNotBlank()) Text(model.saveWarning, color = Gold)
            HorizontalDivider()
            Row(Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("소지품", color = Gold)
                state.inventory.forEach { item ->
                    FilterChip(selected = item in model.selectedItems, onClick = { model.select(item) }, label = { Text(item.label) })
                }
                OutlinedButton(onClick = { model.panel = "items" }, enabled = model.selectedItems.isNotEmpty()) { Text("살펴보기") }
                Button(onClick = model::combine, enabled = model.selectedItems.size == 2) { Text("조합") }
            }
            if (Flag.ACT1_COMPLETE in state.flags) {
                Text("1막 완료 · 감시실의 전원이 살아 있다.\n2·3막은 다음 네이티브 이식 단계입니다.", color = Gold)
            }
        }
        model.panel?.let { panel -> InvestigationPanel(model, panel) }
    }
}

@Composable private fun SceneArtwork(state: GameState, modifier: Modifier) {
    val background = when {
        Flag.ACT1_COMPLETE in state.flags -> "END"
        state.scene == Scene.S02 && Flag.GLOVE_OPEN in state.flags -> "S02-open"
        state.scene == Scene.S05 && state.seat >= 99 -> "S05-forward"
        state.scene == Scene.S06 && Flag.ROOF_OPEN in state.flags -> "S06-open"
        else -> state.scene.name
    }
    Box(modifier.background(Color.Black, RoundedCornerShape(12.dp)).border(1.dp, Teal.copy(alpha = .3f), RoundedCornerShape(12.dp)), contentAlignment = Alignment.Center) {
        AssetImage("assets/backgrounds/$background.png", state.scene.title, Modifier.fillMaxSize())
    }
}

@Composable private fun AssetImage(path: String, description: String, modifier: Modifier) {
    val context = LocalContext.current
    val bitmap by produceState<ImageBitmap?>(null, path) {
        value = null
        value = withContext(Dispatchers.IO) {
            context.assets.open(path).use { BitmapFactory.decodeStream(it)?.asImageBitmap() }
        }
    }
    bitmap?.let { Image(it, description, modifier, contentScale = ContentScale.Fit) }
}

@Composable private fun Investigations(model: GameViewModel) {
    Text("${model.state.scene.title} · 조사 목록", color = Gold)
    fun open(name: String) { model.panel = name }
    when (model.state.scene) {
        Scene.S01 -> {
            Action("와이퍼 흔적 관찰") { open("wiper") }
            Action("프레임과 카메라") { model.act { inspectFrame() } }
            Action("게임 계기판") { open("cluster") }
            Action("게임 룸미러") { open("mirror") }
            Action("USB 포트") { model.act { connectUsb() } }
        }
        Scene.S02 -> {
            Action("글로브박스 열기") { model.act { openGlove() } }
            Action("서랍 내용물 챙기기") { model.act { lootGlove() } }
            Action("인수 기록 읽기") { model.act { readRecord() } }
            Action("선바이저 조사") { model.act { inspectVisor() } }
            Action("유리 흔적 판독부") { open("fan") }
            Action("USB 포트에 리더기 연결") { model.act { connectUsb() } }
        }
        Scene.S03 -> {
            Action("게임 외투 걷기") { model.act { moveCoat() } }
            Action("가방 고정 끈 풀기") { model.act { releaseStrap() } }
            Action("가방을 바닥으로 옮기기") { model.act { moveBag() } }
            Action("가방 내용물 챙기기") { model.act { lootBag() } }
            Action("운전석 아래 공간 조사") { model.act { collectTool() } }
        }
        Scene.S04 -> {
            Action("게임 룸미러 각도") { open("mirror") }
            Action("녹음의 좌우 채널") { open("audio") }
            Action("유리 흔적 판독부") { open("fan") }
        }
        Scene.S05 -> {
            Action("게임 시트 조작") { open("seat") }
            Action("레일 아래 도구 찾기") { model.act { collectTool() } }
        }
        Scene.S06 -> {
            Action("점검 커버 열기") { model.act { openCover() } }
            Action("삼각 도구 끼우기") { model.act { insertTool() } }
            Action("수동 소켓 회전") { open("socket") }
            Action("게임 선루프 열기") { model.act { openRoof() } }
            Action("위쪽 통로로 탈출") { model.act { escape() } }
        }
    }
}

@Composable private fun Action(label: String, enabled: Boolean = true, run: () -> Unit) {
    OutlinedButton(onClick = run, enabled = enabled, modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)) { Text(label) }
}

/** In-window overlay: opening a game panel must not simulate platform focus loss. */
@Composable private fun InvestigationPanel(model: GameViewModel, panel: String) {
    val state = model.state
    Box(Modifier.fillMaxSize().background(Ink.copy(alpha = .96f)).clickable { }, contentAlignment = Alignment.Center) {
        Column(Modifier.widthIn(max = 740.dp).fillMaxWidth().fillMaxHeight(.95f).padding(24.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("M—04 / 조사", color = Gold, modifier = Modifier.weight(1f))
                TextButton(onClick = model::closePanel) { Text("닫기") }
            }
            when (panel) {
                "notebook" -> {
                    Text("진행 수첩", fontSize = 28.sp)
                    if (state.clues.isEmpty()) Text("아직 기록한 단서가 없습니다.")
                    state.clues.forEach { id -> val clue = model.clue(id); Text(clue.first, color = Gold); Text(clue.second); HorizontalDivider() }
                }
                "items" -> {
                    model.selectedItems.forEach { item ->
                        Text(item.label, fontSize = 24.sp)
                        AssetImage("assets/items/${item.asset}.png", item.label, Modifier.fillMaxWidth().height(220.dp))
                    }
                    if (Item.MANUAL in state.inventory && Item.FOLD_NOTE in state.inventory) {
                        Action("안내서 왼쪽 접기") { model.act { fold(true) } }
                        Action("안내서 아래 접기") { model.act { fold(false) } }
                    }
                }
                "wiper", "fan" -> {
                    val puzzle = if (panel == "wiper") InputPuzzle.P01 else InputPuzzle.P05
                    Text(if (panel == "wiper") "앞유리 흔적 관찰" else "유리 흔적 판독부", fontSize = 28.sp)
                    Text("화면 조작 보조 ON · 모의 입력입니다. 실제 차량 장치를 제어하지 않습니다.")
                    Action("단말 활성화") { model.arm(puzzle) }
                    Text(model.inputStatus, color = Teal)
                    if (BuildConfig.SIMULATED_PARKING) {
                        if (panel == "wiper") {
                            Action("와이퍼 정지") { model.simulationValue("wiper", "OFF") }
                            Action("와이퍼 작동") { model.simulationValue("wiper", "ACTIVE") }
                        } else {
                            Action("풍량 낮음") { model.simulationValue("fan", "LOW") }
                            Action("풍량 중간") { model.simulationValue("fan", "MID") }
                        }
                    }
                    Text("같은 값 반복은 다음 단계가 아닙니다. 잠깐 바꾼 상태는 인정하지 않습니다.")
                }
                "mirror" -> {
                    Text("게임 룸미러 · ${state.mirror}°", fontSize = 28.sp)
                    Text("화면 속 거울입니다. 실제 룸미러를 움직일 필요가 없습니다.")
                    Slider(value = state.mirror.toFloat(), onValueChange = { model.act { setMirror(it.toInt()) } }, valueRange = -30f..30f, steps = 59)
                    if (Flag.GLASS_READ in state.flags) Text(model.clue("glass").second, color = Gold)
                    else Text(if (Flag.FOG_RESTORED in state.flags) "희미한 문장과 레일 그림이 반사된다." else "유리 흔적이 흐려 읽을 수 없다.")
                }
                "seat" -> {
                    Text("게임 시트 · ${state.seat}%", fontSize = 28.sp)
                    Text("화면 속 게임 오브젝트만 움직입니다.")
                    Slider(value = state.seat.toFloat(), onValueChange = { model.act { setSeat(it.toInt()) } }, valueRange = 0f..100f, steps = 99)
                }
                "socket" -> {
                    Text("삼각 수동 소켓", fontSize = 28.sp)
                    Text("화면 속 도구입니다. 단서 열람 여부와 관계없이 추리한 순서를 시도할 수 있습니다.")
                    Action("반시계 90°") { model.act { rotate(-90) } }
                    Action("시계 90°") { model.act { rotate(90) } }
                    Action("시계 180°") { model.act { rotate(180) } }
                }
                "audio" -> {
                    Text("녹음 · 좌우 채널", fontSize = 28.sp)
                    if (Flag.USB_CONNECTED !in state.flags) Text("카드와 리더기를 조합해 USB 포트에 연결하세요.")
                    else {
                        Action("왼쪽 채널 재생") { model.play(true) }
                        Action("오른쪽 채널 재생") { model.play(false) }
                        Action("재생 정지") { model.stopAudio() }
                        Text("자막으로도 기록할 수 있습니다. 차량 오디오 밸런스는 변경하지 않습니다.")
                        Action("왼쪽 자막 확인") { model.act { hearChannel(true) } }
                        Action("오른쪽 자막 확인") { model.act { hearChannel(false) } }
                        if (Flag.LEFT_HEARD in state.flags) Text(model.clue("voiceLeft").second)
                        if (Flag.RIGHT_HEARD in state.flags) Text(model.clue("voiceRight").second)
                    }
                }
                "cluster" -> {
                    Text("게임 계기판", fontSize = 28.sp)
                    Text("M—04 / 상태 보류\n금속 프레임이 차량을 둘러싸고 있다. 게임 속의 흔적을 살펴보자.")
                }
            }
            Text(model.message, color = Gold)
        }
    }
}
