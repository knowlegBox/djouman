[Setup]
AppName=Djouman
AppVersion=1.0
DefaultDirName={autopf}\Djouman
DefaultGroupName=Djouman
OutputDir=.\Output
OutputBaseFilename=Djouman
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=assets\icons\app_icon.ico
UninstallDisplayIcon={app}\Djouman.exe

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Djouman\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Djouman"; Filename: "{app}\Djouman.exe"
Name: "{autodesktop}\Djouman"; Filename: "{app}\Djouman.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Djouman.exe"; Description: "{cm:LaunchProgram,Djouman}"; Flags: nowait postinstall skipifsilent
