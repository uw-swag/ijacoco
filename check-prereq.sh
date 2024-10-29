#!/bin/bash

# Check the following prerequisites for running ijacoco experiments:
# conda: for using python scripts
# java (version 8) and mvn (==3.9) for building ijacoco and used java projects
# cloc: for counting lines of code

_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

function main() {
        echo "Checking prerequisites..."

        echo "--- conda ---"
        local conda_installed=false
        local conda_exe=$(which conda)
        if [[ -z ${conda_exe} ]]; then
                echo "❌ Not Found"
                echo "  Hint: please install [Miniconda](https://docs.anaconda.com/free/miniconda/index.html) or Anaconda"
                echo "  Hint: if you have installed conda, try 'conda init' and restart the terminal"
        else
                conda_installed=true
                echo "✅ OK"
                echo "  -> conda executable at ${conda_exe}"
        fi

        echo "--- java ---"
        local java_installed=false
        local java_version_ok=false
        local java_exe=$(which java)
        if [[ -z ${java_exe} ]]; then
                echo "❌ Not Found"
                echo "  Hint: please install Java 8"
                echo "  Hint: [sdkman](https://sdkman.io/) is recommended for installing Java-related tools and managing multiple versions"
                echo "  Hint: once you have sdkman: 'sdk list java' to find a version that starts with 8, 'sdk install java <version>' to install it, and 'sdk use java <version>' to switch to it"
        else
                java_installed=true
                local java_version=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
                if [[ ${java_version} != 1.8.0* ]]; then
                        echo "❓ Wrong Version"
                        echo "  Hint: our code was built with Java 8; it may or may not work with other versions"
                        echo "  Hint: if you use sdkman: 'sdk list java' to find a version that starts with 8, 'sdk install java <version>' to install it, and 'sdk use java <version>' to switch to it"
                        echo "  -> java executable at ${java_exe}"
                        echo "  -> java version: ${java_version}"
                else
                        java_version_ok=true
                        echo "✅ OK"
                        echo "  -> java executable at ${java_exe}"
                        echo "  -> java version: ${java_version}"
                fi
        fi

        echo "--- mvn ---"
        local mvn_installed=false
        local mvn_version_ok=false
        local mvn_exe=$(which mvn)
        if [[ -z ${mvn_exe} ]]; then
                echo "❌ Not Found"
                echo "  Hint: please install Maven 3.9"
                echo "  Hint: [sdkman](https://sdkman.io/) is recommended for installing Java-related tools and managing multiple versions"
                echo "  Hint: once you have sdkman: 'sdk list maven' to find a version that starts with 3.9, 'sdk install maven <version>' to install it, and 'sdk use maven <version>' to switch to it"
        else
                mvn_installed=true
                local mvn_version=$(mvn -version 2>&1 | head -n 1 | cut -d' ' -f3)
                if [[ ${mvn_version} != 3.9.* ]]; then
                        echo "❓ Wrong Version"
                        echo "  Hint: our code was built with Maven 3.9; it may or may not work with other versions"
                        echo "  Hint: if you use sdkman: 'sdk list maven' to find a version that starts with 3.9, 'sdk install maven <version>' to install it, and 'sdk use maven <version>' to switch to it"
                        echo "  -> mvn executable at ${mvn_exe}"
                        echo "  -> mvn version: ${mvn_version}"
                else
                        mvn_version_ok=true
                        echo "✅ OK"
                        echo "  -> mvn executable at ${mvn_exe}"
                        echo "  -> mvn version: ${mvn_version}"
                fi
        fi

        echo "--- cloc ---"
        local cloc_installed=false
        local cloc_exe=$(which cloc)
        if [[ -z ${cloc_exe} ]]; then
                echo "❌ Not Found"
                echo "  Hint: please install cloc"
        else
                cloc_installed=true
                echo "✅ OK"
                echo "  -> cloc executable at ${cloc_exe}"
        fi

        echo
        echo "=== Summary ==="
        if [[ ${conda_installed} == true && ${cloc_installed} == true ]]; then
                if [[ ${java_version_ok} == true && ${mvn_version_ok} == true ]]; then
                        echo "✅ You meet all the prerequisites."
                else
                        if [[ ${java_installed} == true && ${mvn_installed} == true ]]; then
                                echo "❓ You have java and maven but not the correct version. Our code may not work as expected."
                        else
                                echo "❌ You are missing some prerequisites, please check the above messages for details."
                        fi
                fi
        else
                echo "❌ You are missing some prerequisites, please check the above messages for details."
        fi
}

main
