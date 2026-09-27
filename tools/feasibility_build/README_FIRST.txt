FM2001 Modern Port - Feasibility Build 0.1

PURPOSE
This is an early Windows 11 portability/packaging test, not a finished game.

PORTABLE LAYOUT
FM2001.exe
IntroPlayer.exe
Assets\premintro.mp4
GameData\Master.dat
GameData\Static.dat
GameData\English.str
GameData\Core.str
GameData\FOOTBAL.EXE
Saves\

RUN
Double-click FM2001.exe.

The original FM2001 intro plays first when Assets\premintro.mp4 is present.
Press Escape, Space, Enter, or click to skip it.

No installer or administrator rights are intended to be required.
If GameData is missing, the launcher asks you to select an existing FM2001
folder instead.

PC-BANG NOTE
Some managed PCs block unknown executables. If Windows or the venue's security
software prevents FM2001.exe or IntroPlayer.exe from starting, that does not by
itself indicate a port failure.

LIMITATIONS
This build uses the temporary development UI. It exists to validate Windows
packaging, original-data loading, intro playback, gameplay, save/load and the
current reconstructed systems before the original front end is restored.
