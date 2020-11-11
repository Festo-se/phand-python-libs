Add-Type -AssemblyName System.Windows.Forms
$FolderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog -Property @{
    SelectedPath = 'C:\’
}

Write-Host "Select the directory where the libraries should be downloaded and installed into" 

[void]$FolderBrowser.ShowDialog()

Write-Host "Selected" $FolderBrowser.SelectedPath

cd $FolderBrowser.SelectedPath

Write-Host "Checkout the bionic_python_libs repository from Github"

Write-Host "Checkout the phand_python_libs repository from Github"

Write-Host "Checkout the dhcp implementation repository from Github"

Write-Host "Checkout the pid control repository from Github"

Write-Host "Install bionic_python_libs"
pip3 install --editable ./bionic_msg

Write-Host "Install phand_python_libs"
pip3 install --editable ./phand_test

Write-Host "Install dhcp implementation"
pip3 install --editable ./bionic_dhcp

Write-Host "Install pid control implementation"
pip3 install --editable ./bionic_pid_control

read-host “Press any key to quit...”