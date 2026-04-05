plugins {
    kotlin("jvm") version "2.0.21"
    application
}

group = "io.iconoclastaud.horde"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.microsoft.playwright:playwright:1.49.0")
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("io.iconoclastaud.horde.minicon.MiniconExportKt")
}

tasks.named<JavaExec>("run") {
    workingDir = rootProject.projectDir
}
