function webserver {
    param(
        [int]$port=8080,
        [string]$pidfile=".\webserver-$port.pid"
    )
    $PID | Out-File -FilePath $pidfile -Force
    Write-Host "[*] PID $PID saved to $pidfile"
    $s=[Net.HttpListener]::new()
    $s.Prefixes.Add("http://+:$port/")
    $s.Start()
    Write-Host "Listening http://+:$port/ (GET /exit to stop)"
    try {
        while($c=$s.GetContext()){
            $r=$c.Response
            $ip=$c.Request.RemoteEndPoint.Address.IPAddressToString
            $method=$c.Request.HttpMethod
            $url=$c.Request.Url.PathAndQuery
            if($url -eq "/exit"){
                $b=[Text.Encoding]::UTF8.GetBytes("bye")
                $r.ContentLength64=$b.Length
                $r.OutputStream.Write($b,0,$b.Length)
                $r.Close()
                Write-Host "$ip $method $url 3"
                break
            }
            $f="$pwd$($c.Request.Url.LocalPath)"
            try{
                $b=[IO.File]::ReadAllBytes($f)
                $r.ContentLength64=$b.Length
                $r.OutputStream.Write($b,0,$b.Length)
                $size=$b.Length
            }catch{
                $r.StatusCode=404
                $size=0
            }
            $r.Close()
            Write-Host "$ip $method $url $size"
        }
    } finally {
        $s.Stop()
        $s.Close()
        if (Test-Path $pidfile) { Remove-Item $pidfile -Force -ErrorAction SilentlyContinue }
        Write-Host "Server stopped."
    }
}

webserver -port 80
