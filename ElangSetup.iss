; -- ElangSetup.iss --
; Professional Installer for Elang v3.0
; Compile with Inno Setup 6+ (https://jrsoftware.org/isinfo.php)
;
; ✅ Installs elang.exe to Program Files
; ✅ Adds to PATH (with clean removal on uninstall)
; ✅ Associates .elang files (with clean removal on uninstall)
; ✅ Installs VS Code extension (with clean removal on uninstall)
; ✅ Works on fresh Windows — NO Python needed

[Setup]
AppName=Elang Programming Language
AppVersion=3.0
AppPublisher=Eusha
AppPublisherURL=https://github.com/eusha/elang
DefaultDirName={autopf}\Elang
DefaultGroupName=Elang
UninstallDisplayIcon={app}\elang.exe
UninstallDisplayName=Elang Programming Language v3.0
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=ElangSetup
; SetupIconFile=E.ico        ; <-- Uncomment this if you have an .ico file
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
LicenseFile=LICENSE
ChangesEnvironment=yes

[Files]
; The standalone Elang runtime (no Python needed!)
Source: "dist\elang.exe"; DestDir: "{app}"; Flags: ignoreversion

; The VS Code extension VSIX
Source: "eusha-language\elang-language-1.0.0.vsix"; DestDir: "{app}"; Flags: ignoreversion

; Example files
Source: "examples\*"; DestDir: "{app}\examples"; Flags: ignoreversion recursesubdirs

; Docs
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\Elang Examples"; Filename: "{app}\examples"
Name: "{group}\Elang Documentation"; Filename: "{app}\README.md"
Name: "{group}\Uninstall Elang"; Filename: "{uninstallexe}"

[Tasks]
Name: addtopath; Description: "Add Elang to system PATH (recommended)"; Flags: checkedonce
Name: fileassoc; Description: "Associate .elang files with Elang"; Flags: checkedonce
Name: installvscode; Description: "Install VS Code extension (if VS Code is installed)"; Flags: checkedonce

[Registry]
; File association — only if user checked the task
; These are automatically removed on uninstall thanks to 'uninsdeletekeyifempty' and 'uninsdeletevalue'
Root: HKCU; Subkey: "Software\Classes\.elang"; ValueType: string; ValueData: "ElangFile"; Tasks: fileassoc; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\ElangFile"; ValueType: string; ValueData: "Elang Source File"; Tasks: fileassoc; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\ElangFile\DefaultIcon"; ValueType: string; ValueData: "{app}\elang.exe,0"; Tasks: fileassoc; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\ElangFile\shell\open\command"; ValueType: string; ValueData: """{app}\elang.exe"" ""%1"""; Tasks: fileassoc; Flags: uninsdeletekey

[Run]
; Install VS Code extension after setup (only if task selected and 'code' exists)
Filename: "code"; Parameters: "--install-extension ""{app}\elang-language-1.0.0.vsix"" --force"; \
    StatusMsg: "Installing VS Code extension..."; Tasks: installvscode; \
    Flags: nowait runhidden skipifdoesntexist

[UninstallRun]
; Remove VS Code extension on uninstall
Filename: "code"; Parameters: "--uninstall-extension eusha.elang-language"; \
    Flags: nowait runhidden skipifdoesntexist

[Code]
// ============================================================
//  PATH Management — Clean Add & Remove
// ============================================================

procedure AddToPath(Dir: string);
var
  Path: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
    Path := '';
  if Pos(Dir, Path) = 0 then
  begin
    if Path <> '' then
      Path := Path + ';';
    Path := Path + Dir;
    RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path);
  end;
end;

procedure RemoveFromPath(Dir: string);
var
  Path, NewPath: string;
begin
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
  begin
    // Remove ";Dir" or "Dir;" or just "Dir"
    NewPath := Path;
    StringChangeEx(NewPath, ';' + Dir, '', True);
    StringChangeEx(NewPath, Dir + ';', '', True);
    StringChangeEx(NewPath, Dir, '', True);
    if NewPath <> Path then
      RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', NewPath);
  end;
end;

// Called after installation steps complete
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and IsTaskSelected('addtopath') then
    AddToPath(ExpandConstant('{app}'));
end;

// Called during uninstall — removes PATH entry
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RemoveFromPath(ExpandConstant('{app}'));
end;
