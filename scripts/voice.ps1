$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$taskAudioDir = Join-Path $PSScriptRoot '..\public\audio'
[System.IO.Directory]::CreateDirectory($taskAudioDir) | Out-Null
$taskTracks = @(
 @{ File='intro.wav'; Text='At the restaurant. Time to pay.'; Rate=0 },
 @{ File='question.wav'; Text='Which phrase sounds natural?'; Rate=0 },
 @{ File='answer.wav'; Text='The bill, please.'; Rate=-1 },
 @{ File='explain.wav'; Text='Use bill when you ask to pay.'; Rate=0 },
 @{ File='listen.wav'; Text='Listen, then repeat.'; Rate=0 },
 @{ File='repeat.wav'; Text='The bill, please.'; Rate=-2 },
 @{ File='your-turn.wav'; Text='Your turn.'; Rate=0 },
 @{ File='outro.wav'; Text='Try it next time.'; Rate=0 }
)
foreach ($taskTrack in $taskTracks) {
 $taskVoice = New-Object System.Speech.Synthesis.SpeechSynthesizer
 try {
  $taskVoice.SelectVoice('Microsoft Zira Desktop')
  $taskVoice.Rate = $taskTrack.Rate
  $taskVoice.Volume = 100
  $taskVoice.SetOutputToWaveFile((Join-Path $taskAudioDir $taskTrack.File))
  $taskVoice.Speak($taskTrack.Text)
  $taskVoice.SetOutputToNull()
 } finally { $taskVoice.Dispose() }
}
Write-Output '8 English test voice tracks generated.'
