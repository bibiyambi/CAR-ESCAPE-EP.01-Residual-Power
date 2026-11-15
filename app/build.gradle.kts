import com.android.build.api.dsl.ApplicationExtension
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    kotlin("android")
    id("org.jetbrains.kotlin.plugin.compose")
}
extensions.configure<ApplicationExtension> {
    namespace = "io.bibiyambi.residualpower"
    compileSdk = 37
    defaultConfig {
        applicationId = "io.bibiyambi.residualpower"
        minSdk = 28
        // API 37 is intentional; review runtime behavior when testing on Android 17.
        //noinspection EditedTargetSdkVersion
        targetSdk = 37
        versionCode = 1
        versionName = "0.1.0-native"
    }
    flavorDimensions += "runtime"
    productFlavors {
        create("development") {
            dimension = "runtime"
            applicationIdSuffix = ".development"
            buildConfigField("boolean", "SIMULATED_PARKING", "true")
        }
        create("pleos") {
            dimension = "runtime"
            buildConfigField("boolean", "SIMULATED_PARKING", "false")
        }
    }
    buildTypes { release { isMinifyEnabled = false } }
    buildFeatures { compose = true; buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    useLibrary("android.car")
}
kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}
androidComponents {
    onVariants { variant ->
        variant.sources.assets?.addStaticSourceDirectory(
            layout.buildDirectory.dir("generated/nativeAssets").get().asFile.absolutePath,
        )
    }
}
val prepareNativeAssets = tasks.register<Exec>("prepareNativeAssets") {
    description = "Prepares game assets for packaging in the Android app."
    workingDir(rootDir)
    commandLine("python3", "tools/prepare_assets.py", "--source", providers.gradleProperty("gameSource").orElse("../CAR-ESCAPE-EP.01-Residual-Power-source/261115-개발자료모음/잔류전원_3막_소스팩").get())
}
tasks.named("preBuild") { dependsOn(prepareNativeAssets) }
dependencies {
    implementation(project(":core"))
    implementation(platform("androidx.compose:compose-bom:2026.09.00"))
    implementation("androidx.activity:activity-compose:1.13.0")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.11.0")
    add("pleosImplementation", "ai.pleos.playground:Vehicle:2.3.2")
}
