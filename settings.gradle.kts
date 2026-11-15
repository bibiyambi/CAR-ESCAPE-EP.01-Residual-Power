pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.10.0"
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google(); mavenCentral()
        exclusiveContent {
            forRepository { maven("https://nexus-playground.pleos.ai/repository/maven-releases/") }
            filter { includeGroupByRegex("ai\\.pleos\\..*") }
        }
    }
}
rootProject.name = "ResidualPower"
include(":app", ":core")
