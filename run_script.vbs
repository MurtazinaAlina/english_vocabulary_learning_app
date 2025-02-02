Set objShell = CreateObject("WScript.Shell")

' Получаем путь к текущей папке скрипта
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Подставляем путь в команду
batFilePath = strPath & "\run_script.bat"

' Запускаем команду
objShell.Run "cmd /c """ & batFilePath & """", 0, False