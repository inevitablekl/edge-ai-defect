#include <cstdlib>

static_assert(__cplusplus == 201703L, "The project must compile as C++17");

int main() {
    return __cplusplus == 201703L ? EXIT_SUCCESS : EXIT_FAILURE;
}
