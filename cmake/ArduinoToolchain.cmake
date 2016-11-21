

# This one is important, don't set to Linux, otherwise it will failed and report:
# "unrecognized command line option ‘-rdynamic’" !
set(CMAKE_SYSTEM_NAME Generic)

# Specify the cross compiler
set(CMAKE_CXX_COMPILER "${ARDUINO_COMPILER_BASE_PATH}${ARDUINO_CXX_COMPILER_CMD}")
set(CMAKE_C_COMPILER "${ARDUINO_COMPILER_BASE_PATH}${ARDUINO_C_COMPILER_CMD}")

# Where is the target environment
set(CMAKE_FIND_ROOT_PATH  "${ARDUINO_AVR_GCC_ROOT_PATH}")

# Search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# For libraries and headers in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

