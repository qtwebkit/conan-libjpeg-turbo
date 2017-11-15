cmake_minimum_required(VERSION 2.8.12)

project(cmake_wrapper)

include(${CMAKE_CURRENT_SOURCE_DIR}/../conanbuildinfo.cmake)
conan_basic_setup()

include(CMakeLists_original.txt)
