; ==============================================================================
; YoloSide v2.0 — Inno Setup Installer Script (中文安装界面)
; ==============================================================================
; Prerequisites: Inno Setup 6.x  (D:\Software\Inno Setup 6\ISCC.exe)
;
; Build (after PyInstaller has produced dist\YoloSide\):
;   iscc installer.iss
;   → Output: dist\YoloSide_Setup_v2.0.exe
;
; 产物: 单个 exe，用户双击 → 选择安装路径 → 自动完成安装
;       桌面快捷方式 + 开始菜单 + 卸载程序 全自动配置
; ==============================================================================

#define AppName       "YoloSide"
#define AppVersion    "2.0"
#define AppPublisher  "YoloSide"
#define AppExeName    "YoloSide.exe"
#define AppIcoName    "img\logo.ico"
#define OutputDir     "dist"

[Setup]
AppId                    = {{B8A1F2C3-D4E5-6789-ABCD-EF0123456789}
AppName                  = {#AppName}
AppVersion               = {#AppVersion}
AppPublisher             = {#AppPublisher}
VersionInfoVersion       = {#AppVersion}.0.0
VersionInfoDescription   = YoloSide — Ultralytics Desktop GUI
VersionInfoCopyright     = (c) 2026 {#AppPublisher}

; 默认安装到 %LOCALAPPDATA%\Programs (无需管理员权限)
DefaultDirName           = {localappdata}\Programs\{#AppName}
; SourceDir removed — use explicit path in [Files] Source instead
OutputDir                = {#OutputDir}
OutputBaseFilename       = YoloSide_Setup_v{#AppVersion}

; 最高压缩率
Compression              = lzma2/ultra64
SolidCompression         = yes
LZMADictionarySize       = 65536
LZMAUseSeparateProcess   = yes

; 现代化安装向导界面
SetupIconFile            = {#AppIcoName}
WizardStyle              = modern
WizardSizePercent        = 120,140
DisableWelcomePage       = no
DisableProgramGroupPage  = auto
AllowNoIcons             = yes

; 用户级安装 (无需管理员，%LOCALAPPDATA% 始终可写)
PrivilegesRequired       = none

; 卸载信息
UninstallDisplayIcon     = {app}\{#AppExeName}
UninstallDisplayName     = {#AppName} v{#AppVersion}
; UninstallDisplaySize intentionally left blank (auto-calculated)

; 64位
ArchitecturesAllowed     = x64compatible
ArchitecturesInstallIn64BitMode = x64compatible

; ── 语言: 使用 Default.isl 作为基底，通过 [CustomMessages] 汉化 ──
[Languages]
Name: "chinese"; MessagesFile: "compiler:Default.isl"

; ══════════════════════════════════════════════════════════════════════
; 完整中文界面覆盖 (基于 Inno Setup Default.isl 消息 ID)
; ══════════════════════════════════════════════════════════════════════

[CustomMessages]
; ── 通用按钮 ────────────────────────────────────────────────────────
chinese.ButtonBack             = < 上一步(&B)
chinese.ButtonNext             = 下一步(&N) >
chinese.ButtonInstall          = 安装(&I)
chinese.ButtonCancel           = 取消
chinese.ButtonFinish           = 完成(&F)
chinese.ButtonYes              = 是(&Y)
chinese.ButtonNo               = 否(&N)
chinese.ButtonOK               = 确定
chinese.ButtonBrowse            = 浏览(&B)...
chinese.ButtonWizard            = 上一步(&B)
chinese.ExitSetupTitle          = 退出安装程序
chinese.ExitSetupMessage        = 安装尚未完成。如果现在退出，程序将不会被安装。%n%n您可以稍后再次运行安装程序以完成安装。%n%n确定要退出吗？
chinese.AboutSetupMenuItem      = 关于安装程序(&A)...

; ── 欢迎页面 ────────────────────────────────────────────────────────
chinese.WelcomeLabel1           = 欢迎安装 {#AppName} v{#AppVersion}
chinese.WelcomeLabel2           = 本安装程序将在您的计算机上安装 {#AppName}。%n%n{#AppName} 是 ultralytics YOLO 框架的桌面图形界面，支持检测、分割、姿态估计、分类、旋转目标检测(OBB)及目标跟踪。%n%n推荐在继续安装前关闭所有其他应用程序。

; ── 许可协议页面 (跳过，没有 LICENSE 展示需求) ──────────────────────

; ── 选择安装目录页面 ────────────────────────────────────────────────
chinese.SelectDirLabel1         = 请选择 {#AppName} 的安装目录。
chinese.SelectDirLabel2         = 程序将安装到以下文件夹。%n%n如需安装到其他文件夹，请点击"浏览"选择。
chinese.SelectDirBrowseLabel    = 选择安装目录
chinese.DiskSpaceMBLabel        = 至少需要 [mb] MB 可用磁盘空间。
chinese.ToUNCPathname           = 您输入了一个 UNC 路径，将使用其映射的盘符。
chinese.InvalidPath             = 您输入的路径无效，请输入有效的路径。
chinese.DirExists               = 目标文件夹已存在：%n%n%1%n%n是否仍要安装到该文件夹？
chinese.DirDoesntExist          = 文件夹 %1 不存在，是否创建？

; ── 选择开始菜单文件夹页面 ──────────────────────────────────────────
chinese.SelectProgramGroupLabel1= 请选择安装程序创建快捷方式的开始菜单文件夹。
chinese.SelectProgramGroupLabel2= 开始菜单文件夹：
chinese.SelectStartMenuFolderDesc= 安装程序将在以下开始菜单文件夹中创建快捷方式，您可以输入新名称或从列表中选择。

; ── 准备安装页面 ────────────────────────────────────────────────────
chinese.ReadyLabel1             = 安装程序准备就绪，将开始安装 {#AppName}。
chinese.ReadyLabel2a            = 点击"安装"开始安装，或点击"上一步"查看或修改设置。
chinese.ReadyLabel2b            = 安装目录：
chinese.ReadyMemoEmpty1         = 未检测到需要执行的附加任务。
chinese.ReadyMemoEmpty2         = 点击"安装"开始安装。
chinese.ClickInstall            = 点击"安装"开始。
chinese.ClickNext               = 点击"下一步"继续。
chinese.ClickFinish             = 点击"完成"退出安装程序。

; ── 安装进度页面 ────────────────────────────────────────────────────
chinese.InstallingLabel         = 正在安装 {#AppName}，请稍候...
chinese.FinishedLabel1          = {#AppName} 安装完成！
chinese.FinishedLabel2          = {#AppName} 已成功安装到您的计算机。%n%n点击"完成"退出安装程序。
chinese.FinishedHeadingLabel    = 安装完成

; ── 完成后运行 ──────────────────────────────────────────────────────
chinese.LaunchProgram           = 立即运行 {#AppName}

; ── 状态消息 ────────────────────────────────────────────────────────
chinese.SetupWindowTitle        = 安装 — {#AppName} v{#AppVersion}
chinese.UninstallAppFullTitle   = 卸载 — {#AppName}
chinese.SetupAppRunningError    = 检测到 {#AppName} 正在运行。%n%n请先关闭程序，然后点击"确定"继续。
chinese.SetupFileMissing        = 安装包中缺少文件: %1。请重新下载安装程序。
chinese.InstallingLabelShort    = 安装中...
chinese.UninstallingLabel       = 正在卸载 {#AppName}，请稍候...
chinese.FileAbortRetryIgnore    = 文件 %1 无法被写入。%n%n请确认文件未被其他程序占用，然后重试。
chinese.FinishedRestartLabel    = 要完成安装，必须重启计算机。%n%n现在重启？

; ── 卸载程序 ────────────────────────────────────────────────────────
chinese.ConfirmUninstall        = 确定要完全卸载 {#AppName} 吗？%n%n所有程序文件及下载的模型都将被删除。
chinese.UninstallStatusLabel    = 正在卸载，请稍候...
chinese.UninstalledAll          = {#AppName} 已从您的计算机中移除。
chinese.UninstalledMost         = 卸载完成。%n%n部分文件未能删除，您可以手动删除安装目录。

; ── 错误信息 ────────────────────────────────────────────────────────
chinese.ErrorCreatingDir        = 无法创建目录 %1
chinese.ErrorTooManyFilesInDir  = 目录中的文件过多: %1

; ══════════════════════════════════════════════════════════════════════
; 文件安装
; ══════════════════════════════════════════════════════════════════════

[Files]
Source: "dist\YoloSide\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; ══════════════════════════════════════════════════════════════════════
; 快捷方式
; ══════════════════════════════════════════════════════════════════════

[Icons]
; 桌面快捷方式
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"; \
  Comment: "YoloSide — Ultralytics Desktop GUI"
; 开始菜单
Name: "{autoprograms}\{#AppName}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
  WorkingDir: "{app}"; IconFilename: "{app}\{#AppExeName}"
; 开始菜单 → 卸载
Name: "{autoprograms}\{#AppName}\卸载 YoloSide"; Filename: "{uninstallexe}"

; ══════════════════════════════════════════════════════════════════════
; 安装后 (可选) 运行
; ══════════════════════════════════════════════════════════════════════

[Run]
Filename: "{app}\{#AppExeName}"; \
  Description: "{cm:LaunchProgram,{#AppName}}"; \
  Flags: nowait postinstall skipifsilent

; ══════════════════════════════════════════════════════════════════════
; 确保数据目录存在且可写
; ══════════════════════════════════════════════════════════════════════

[Dirs]
Name: "{app}\models"; Permissions: users-full
Name: "{app}\config"; Permissions: users-full
Name: "{app}\runs";   Permissions: users-full

; ══════════════════════════════════════════════════════════════════════
; 卸载时清理所有用户数据
; ══════════════════════════════════════════════════════════════════════

[UninstallDelete]
Type: filesandordirs; Name: "{app}\models"
Type: filesandordirs; Name: "{app}\config"
Type: filesandordirs; Name: "{app}\runs"
Type: dirifempty;    Name: "{app}"
