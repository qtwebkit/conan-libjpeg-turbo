#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools


class LibjpegTurboConan(ConanFile):
    name = "libjpeg-turbo"
    version = "1.5.2"
    description = "SIMD-accelerated libjpeg-compatible JPEG codec library"
    url = "http://github.com/bincrafters/conan-libjpeg-turbo"
    homepage = "https://libjpeg-turbo.org"
    license = "BSD 3-Clause, ZLIB"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "SSE": [True, False]}
    default_options = "shared=False", "fPIC=True", "SSE=True"
    source_subfolder = "source_subfolder"

    def config(self):
        del self.settings.compiler.libcxx

        if self.settings.os == "Windows":
            self.requires.add("nasm/2.13.01@conan/stable", private=True)
        if self.settings.compiler == "Visual Studio":
            self.options.remove("fPIC")

    def source(self):
        tools.get("http://downloads.sourceforge.net/project/libjpeg-turbo/%s/libjpeg-turbo-%s.tar.gz" % (self.version, self.version))
        os.rename("libjpeg-turbo-%s" % self.version, self.source_subfolder)
        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeLists_original.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build_configure(self):
        prefix = os.path.abspath(self.package_folder)
        with tools.chdir(self.source_subfolder):
            # works for unix and mingw environments
            env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os == 'Windows')
            env_build.fpic = self.options.fPIC
            if self.settings.os == 'Windows':
                prefix = tools.unix_path(prefix)
            args = ['--prefix=%s' % prefix]
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])

            if self.settings.os == "Macos":
                tools.replace_in_file("configure",
                                      r'-install_name \$rpath/\$soname',
                                      r'-install_name \$soname')

            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build_cmake(self):
        # fix cmake that gather install targets from the wrong dir
        for bin_program in ['tjbench', 'cjpeg', 'djpeg', 'jpegtran']:
            tools.replace_in_file("%s/CMakeLists_original.txt" % self.source_subfolder,
                                  '${CMAKE_CURRENT_BINARY_DIR}/' + bin_program + '-static.exe',
                                  '${CMAKE_CURRENT_BINARY_DIR}/bin/' + bin_program + '-static.exe')
        cmake = CMake(self)
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['WITH_SIMD'] = self.options.SSE
        cmake.configure(source_dir=self.source_subfolder)
        cmake.build()
        cmake.install()

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_cmake()
        else:
            self.build_configure()

    def package(self):
        # remove unneeded directories
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'man'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.package_folder, 'share', 'doc'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.package_folder, 'doc'), ignore_errors=True)

        # remove binaries
        for bin_program in ['cjpeg', 'djpeg', 'jpegtran', 'tjbench', 'wrjpgcom', 'rdjpgcom']:
            for ext in ['', '.exe']:
                try:
                    os.remove(os.path.join(self.package_folder, 'bin', bin_program+ext))
                except:
                    pass

        self.copy("license*", src=self.source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        # Copying generated header
        if self.settings.compiler == "Visual Studio":
            self.copy("jconfig.h", dst="include", src=".")

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ['jpeg', 'turbojpeg']
            else:
                self.cpp_info.libs = ['jpeg-static', 'turbojpeg-static']
        else:
            self.cpp_info.libs = ['jpeg', 'turbojpeg']
