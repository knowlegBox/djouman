; =====================================================================
; Script d'installation Inno Setup pour Djuma (Todo List Manager)
; =====================================================================

#define MyAppName "Djuma"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "TodoListApp"
#define MyAppExeName "Djuma.exe"

[Setup]
; Identifiant unique pour l'application
AppId={{D3J0UMAN-TODO-LIST-APP-GUID}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Répertoire où le fichier d'installation (Setup.exe) sera généré
OutputDir=installer_output
OutputBaseFilename=Setup_Djuma_v{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

; Langue du programme d'installation
[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart"; Description: "Lancer Djuma automatiquement au démarrage de Windows"; GroupDescription: "Options de démarrage:"; Flags: unchecked

[Files]
; Inclusion du binaire généré par PyInstaller
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Clé de registre pour le démarrage automatique au boot si l'utilisateur coche la case
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autostart; Flags: uninsdeletevalue

[Run]
; Option pour lancer l'application immédiatement après l'installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
