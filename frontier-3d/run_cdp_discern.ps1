$port = 9225
$chromePath = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$dataDir = "$env:TEMP\chrome_discern_data"

# Launch temporary headless Chrome instance with remote debugging port
$proc = Start-Process -FilePath $chromePath -ArgumentList "--headless=new", "--remote-debugging-port=$port", "--user-data-dir=$dataDir", "--disable-gpu-shader-disk-cache" -PassThru
Start-Sleep -Seconds 2

try {
    # 1. Discern index.html
    $tab1 = Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$port/json/new?http://127.0.0.1:8799/index.html"
    Start-Sleep -Seconds 3

    $ws1 = New-Object System.Net.WebSockets.ClientWebSocket
    $ct = New-Object System.Threading.CancellationToken
    $ws1.ConnectAsync((New-Object System.Uri($tab1.webSocketDebuggerUrl)), $ct).Wait(4000) | Out-Null

    $eval1 = @{
        id = 1
        method = 'Runtime.evaluate'
        params = @{
            expression = @"
(() => {
    return {
        title: document.title,
        fpsReadout: document.getElementById('fps-readout')?.textContent,
        glbStatus: document.getElementById('glb-status')?.textContent,
        selectedMesh: document.getElementById('selected-mesh-name')?.textContent,
        tokensSaved: document.getElementById('val-tokens-saved')?.textContent,
        ambientCanvasPresent: !!document.getElementById('ponytail-ambient-canvas'),
        ambientWidth: document.getElementById('ponytail-ambient-canvas')?.clientWidth,
        ambientRate: document.getElementById('ambient-rate')?.textContent,
        subActiveTitle: document.getElementById('sub-active-title')?.textContent,
        subWatchdog: document.getElementById('sub-meta-watchdog')?.textContent,
        manifestRowCount: document.querySelectorAll('.manifest-table tbody tr').length,
        canvasWidth: document.getElementById('kronos-canvas')?.clientWidth,
        canvasHeight: document.getElementById('kronos-canvas')?.clientHeight
    };
})()
"@
            returnByValue = $true
        }
    } | ConvertTo-Json -Compress

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($eval1)
    $ws1.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait(2000) | Out-Null
    $buf = New-Object byte[] 65536
    $res = $ws1.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)), $ct)
    $res.Wait(5000) | Out-Null
    $resStr = [System.Text.Encoding]::UTF8.GetString($buf, 0, $res.Result.Count)
    Write-Host "--- DISCERN STREAM: INDEX.HTML RUNTIME STATE ---"
    Write-Host $resStr

    # Test click on Stator_Mid row via DOM click
    $evalClick = @{
        id = 2
        method = 'Runtime.evaluate'
        params = @{
            expression = @"
(() => {
    const row = document.querySelector('tr[data-mesh="SM_Kronos_Stator_Mid"]');
    if (row) row.click();
    return {
        clicked: !!row,
        selectedMesh: document.getElementById('selected-mesh-name')?.textContent,
        subActiveTitle: document.getElementById('sub-active-title')?.textContent,
        subActiveStatus: document.getElementById('sub-active-status')?.textContent
    };
})()
"@
            returnByValue = $true
        }
    } | ConvertTo-Json -Compress

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($evalClick)
    $ws1.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait(2000) | Out-Null
    $buf = New-Object byte[] 65536
    $res = $ws1.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)), $ct)
    $res.Wait(5000) | Out-Null
    Write-Host "--- DISCERN STREAM: SUB-ASSEMBLY CLICK RESPONSE ---"
    Write-Host ([System.Text.Encoding]::UTF8.GetString($buf, 0, $res.Result.Count))

    $ws1.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, '', $ct).Wait(1000) | Out-Null

    # 2. Discern implementation-3d-flowchart.html
    $tab2 = Invoke-RestMethod -Method Put -Uri "http://127.0.0.1:$port/json/new?http://127.0.0.1:8799/implementation-3d-flowchart.html"
    Start-Sleep -Seconds 3

    $ws2 = New-Object System.Net.WebSockets.ClientWebSocket
    $ws2.ConnectAsync((New-Object System.Uri($tab2.webSocketDebuggerUrl)), $ct).Wait(4000) | Out-Null

    $eval2 = @{
        id = 3
        method = 'Runtime.evaluate'
        params = @{
            expression = @"
(() => {
    return {
        title: document.title,
        hudActiveNode: document.getElementById('hud-active-node')?.textContent,
        hudTelemetry: document.getElementById('hud-telemetry')?.textContent,
        svgRotorCount: document.querySelectorAll('.svg-rotor').length,
        svgPackets: [0,1,2,3,4].map(i => ({ id: i, cx: document.getElementById('svg-pkt-' + i)?.getAttribute('cx') })),
        canvasWidth: document.getElementById('webgl-flowchart')?.clientWidth,
        canvasHeight: document.getElementById('webgl-flowchart')?.clientHeight
    };
})()
"@
            returnByValue = $true
        }
    } | ConvertTo-Json -Compress

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($eval2)
    $ws2.SendAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct).Wait(2000) | Out-Null
    $buf = New-Object byte[] 65536
    $res = $ws2.ReceiveAsync((New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)), $ct)
    $res.Wait(5000) | Out-Null
    Write-Host "--- DISCERN STREAM: IMPLEMENTATION FLOWCHART RUNTIME STATE ---"
    Write-Host ([System.Text.Encoding]::UTF8.GetString($buf, 0, $res.Result.Count))

    $ws2.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, '', $ct).Wait(1000) | Out-Null

} finally {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
