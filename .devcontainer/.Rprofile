# # Configure reticulate to use the conda environment by default
# if (requireNamespace("reticulate", quietly = TRUE)) {
#   reticulate::use_condaenv("bioinfo_env", required = TRUE)
#   # Optional: Print the current Python configuration
#   cat("Reticulate is using Python from:", reticulate::py_config()$python, "\n")
# }

# Source: https://renkun.me/2020/04/14/writing-r-in-vscode-working-with-multiple-r-sessions/
Sys.setenv(TERM_PROGRAM = "vscode")
source(file.path(
    Sys.getenv(
        if (.Platform$OS.type == "windows") "USERPROFILE" else "HOME"
    ),
    ".vscode-R", "init.R"
))

# Source: https://github.com/REditorSupport/vscode-R/wiki/Plot-viewer#svg-in-httpgd-webpage
if (interactive() && Sys.getenv("TERM_PROGRAM") == "vscode") {
    if ("httpgd" %in% .packages(all.available = TRUE)) {
        options(vsc.plot = FALSE)
        options(device = function(...) {
            # Set Arial as default font family for httpgd
            httpgd::hgd(
                system_fonts = list(
                    sans = "Arial",
                    serif = "Arial",
                    mono = "Arial"
                )
            )
            .vsc.browser(httpgd::hgd_url(history = FALSE), viewer = "Beside")
        })
    }
}
