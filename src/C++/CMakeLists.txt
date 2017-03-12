cmake_minimum_required(VERSION 3.6)
project(C__)

set(CMAKE_CXX_STANDARD 14)

set(SOURCE_FILES main.cpp GuidanceComputer.cpp GuidanceComputer.h Config.cpp Config.h)
add_executable(C__ ${SOURCE_FILES})