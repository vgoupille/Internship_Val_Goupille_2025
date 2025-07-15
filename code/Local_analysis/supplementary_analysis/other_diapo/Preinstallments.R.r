# This was test on a vanilla Windows machine, installing R version 4.4.1, RStudio and the packages from zero. 
# This should work for both Windows and Mac users. Although, Windows machines might need to install an appropriate version
# of RTools, based on their R version. 

# Pacman package checks versions of already installed packages, downloads uninstalled packages and updates 
# install packages to the minimum version require. If package version is newer, no actions are taken.

# Option with minimum versions.
# IF IT IS NOT INSTALLED, RTOOLS HAS TO BE INSTALLED ON WINDOWS MACHINES
# Depending on your R version, you will need to install the equivalent RTools version (e.g. For R 4.4.x, you need to RTools44)
# It can take a bit to install everything, maybe run before the course starts.

EI_SC_bioinfomatics_package_instalation <- function(){
  if (!require("pacman", quietly = TRUE)){
    install.packages("pacman")
  }
  library(pacman)
  pacman::p_install_version(c("ggplot2", "Seurat", "cowplot", "dplyr", "rmarkdown", "igraph", "devtools"),
                            c("3.5.1", "5.1.0", "1.1.3", "1.1.4", "2.27", "2.0.3", "2.4.5"))
  pacman::p_install_version_gh(c("cole-trapnell-lab/monocle3"),
                               c("1.3.7"))
}

## Running the function
EI_SC_bioinfomatics_package_instalation()
