[Setup]
; Informations generales sur l'application
AppName=Djuma
AppVersion=1.0.0
AppPublisher=KnowlegBox
AppSupportURL=https://github.com/knowlegBox/djouman
AppUpdatesURL=https://github.com/knowlegBox/djouman

; Dossier d'installation par defaut (C:\Users\...\AppData\Local\Programs\Djuma pour l'utilisateur courant, sans besoin d'admin)
DefaultDirName={autopf}\Djuma
DefaultGroupName=Djuma
DisableProgramGroupPage=yes

; Repertoire de sortie pour le fichier Setup.exe
OutputDir=dist
OutputBaseFilename=Djuma_Setup
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes

; Requis pour s'installer sans les droits d'administrateur
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Creer un raccourci sur le Bureau"; GroupDescription: "Raccourcis supplementaires:"

[Files]
; L'executable genere par PyInstaller
Source: "dist\Djuma.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Raccourci dans le menu Demarrer
Name: "{group}\Djuma"; Filename: "{app}\Djuma.exe"
; Raccourci sur le bureau
Name: "{autodesktop}\Djuma"; Filename: "{app}\Djuma.exe"; Tasks: desktopicon

[Run]
; Option pour lancer l'application a la fin de l'installation
Filename: "{app}\Djuma.exe"; Description: "Lancer Djuma"; Flags: nowait postinstall skipifsilent
