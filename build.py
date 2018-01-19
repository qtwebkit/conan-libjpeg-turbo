#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bincrafters import build_template_default
import platform

if __name__ == "__main__":

    builder = build_template_default.get_builder(pure_c=False)
    
    builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        # skip mingw cross-builds
        if not (platform.system() == "Windows" and settings["compiler"] == "gcc" and settings["arch"] == "x86"):
            builds.append([settings, options, env_vars, build_requires])
    builder.builds = builds

    builder.run()
