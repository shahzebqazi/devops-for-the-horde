package io.iconoclastaud.horde.minicon

import com.microsoft.playwright.Page
import com.microsoft.playwright.Playwright
import java.io.File
import java.nio.file.Paths
import kotlin.system.exitProcess

/**
 * Rasterizes HTML/CSS minicons under [docs/assets/minicons] to PNGs in [docs/assets/minicons/png].
 *
 * Variants per source file:
 * - `transparent` — alpha background (omit background)
 * - `clear` — light “mist” backdrop (see minicons.css)
 * - `black` — solid black backdrop
 */
fun main() {
    val repoRoot = findRepoRoot()
    val miniconDir = File(repoRoot, "docs/assets/minicons")
    val outDir = File(repoRoot, "docs/assets/minicons/png")
    outDir.mkdirs()

    val htmlFiles =
        miniconDir
            .listFiles { f -> f.isFile && f.extension.equals("html", ignoreCase = true) }
            ?.sortedBy { it.name }
            .orEmpty()

    if (htmlFiles.isEmpty()) {
        System.err.println("No HTML minicons in ${miniconDir.absolutePath}")
        exitProcess(1)
    }

    Playwright.create().use { playwright ->
        val browser = playwright.chromium().launch()
        val page = browser.newPage()
        page.setViewportSize(256, 256)

        for (html in htmlFiles) {
            val base = html.nameWithoutExtension
            val url = html.toURI().toString()
            for (bg in listOf("transparent", "clear", "black")) {
                page.navigate(url)
                page.evaluate("document.documentElement.setAttribute('data-export-bg', '$bg')")
                page.waitForTimeout(200)
                val target = Paths.get(outDir.absolutePath, "$base-$bg.png")
                val opts =
                    Page.ScreenshotOptions()
                        .setPath(target)
                        .setOmitBackground(bg == "transparent")
                page.screenshot(opts)
                println("Wrote ${repoRoot.toPath().relativize(target)}")
            }
        }
        browser.close()
    }
}

private fun findRepoRoot(): File {
    var dir = File(System.getProperty("user.dir") ?: ".").canonicalFile
    repeat(8) {
        val candidate = File(dir, "docs/assets/minicons")
        if (candidate.isDirectory) {
            return dir
        }
        dir = dir.parentFile ?: break
    }
    error("Could not find repo root containing docs/assets/minicons (from ${System.getProperty("user.dir")})")
}
