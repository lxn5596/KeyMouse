#define MyAppName "键鼠侦测"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "元析科技"
#define MyAppURL "https://yuansio.com"
#define MyAppExeName "keymouse.exe"

[Setup]
AppId={{F8E7C5D3-9B4A-4E8F-B5A1-D2C9E6C3A8B4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=KeyMouse-Setup
SetupIconFile=src\assets\icon.ico
UninstallDisplayIcon={app}\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
; 安全相关设置
CloseApplications=yes
RestartApplications=no
AllowRootDirectory=no
DisableDirPage=no
DisableProgramGroupPage=no
DisableReadyPage=no
DisableFinishedPage=no
DisableWelcomePage=no
EnableDirDoesntExistWarning=yes
DirExistsWarning=yes
; 添加版本信息
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName}
VersionInfoTextVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2024 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
; 使用内置的中文语言文件
UsePreviousLanguage=no

[Languages]
Name: "chinesesimp"; MessagesFile: "ChineseSimplified.isl"

[Messages]
SetupAppTitle=安装 {#MyAppName}
SetupWindowTitle=安装 - {#MyAppName}
WelcomeLabel1=欢迎使用 {#MyAppName} 安装向导
WelcomeLabel2=这将在您的计算机上安装 {#MyAppName}。%n%n建议您在继续之前关闭所有其他应用程序。
ClickNext=点击"下一步"继续，或点击"取消"退出安装程序。
ButtonInstall=安装(&I)
ButtonCancel=取消(&C)
ButtonFinish=完成(&F)
FinishedHeadingLabel=完成 {#MyAppName} 安装
FinishedLabel=安装程序已完成 {#MyAppName} 的安装。应用程序可以通过选择已创建的快捷方式来启动。
ClickFinish=点击"完成"退出安装程序。

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "开机自启动"; GroupDescription: "其他选项:"; Flags: unchecked

[Files]
Source: "dist\keymouse\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\keymouse\keymouse.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "src\assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon

[Registry]
Root: HKCU; Subkey: "Software\KeyMouse"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\KeyMouse"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\KeyMouse"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
; 添加信任信息
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{#MyAppURL}"
Root: HKCU; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\icon.ico"
; 开机启动
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: startupicon; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  // 检查是否有旧版本正在运行
  if CheckForMutexes('Global\KeyMouse') then
  begin
    if MsgBox('检测到程序正在运行。' + #13#10 + '是否关闭程序并继续安装？', 
      mbConfirmation, MB_YESNO) = IDYES then
    begin
      Result := True;
    end
    else
      Result := False;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateDir(ExpandConstant('{userappdata}\.keymouse'));
  end;
end; 