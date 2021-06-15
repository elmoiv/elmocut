#include <stdlib.h>
#include <windows.h>

int main()
{
    // Hide Console Window
    ShowWindow(GetConsoleWindow(), SW_HIDE);
    
    // Start elmocut.exe in a detached process
    system("start \"\" elmocut");
    return 0;
}