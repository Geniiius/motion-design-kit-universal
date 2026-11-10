<#
  Voz local de Windows con marcas reales de palabra y visema (System.Speech, sin red ni coste).
  Escribe un WAV y un JSON: { voice, culture, words: [{text,start}], visemes: [{id,start,duration}] }
#>
param(
  [Parameter(Mandatory)] [string]$TextFile,
  [Parameter(Mandatory)] [string]$Wav,
  [Parameter(Mandatory)] [string]$Json,
  [string]$Culture = "",
  [int]$Rate = 0
)
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech
Add-Type -ReferencedAssemblies System.Speech, System.Collections -TypeDefinition @"
using System; using System.Collections.Generic; using System.Globalization; using System.Text; using System.Speech.Synthesis;
public static class Marcas {
  static readonly object L = new object();
  static readonly List<string> W = new List<string>(), V = new List<string>();
  static string F(double s) { return s.ToString("0.000", CultureInfo.InvariantCulture); }
  static string Q(string s) { return "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\""; }
  public static void Unir(SpeechSynthesizer s) {
    s.SpeakProgress += (a, e) => { lock (L) { W.Add("{\"text\":" + Q(e.Text) + ",\"pos\":" + e.CharacterPosition + ",\"start\":" + F(e.AudioPosition.TotalSeconds) + "}"); } };
    s.VisemeReached += (a, e) => { lock (L) { V.Add("{\"id\":" + e.Viseme + ",\"start\":" + F(e.AudioPosition.TotalSeconds) + ",\"duration\":" + F(e.Duration.TotalSeconds) + "}"); } };
  }
  public static string Json(string voz, string cultura) {
    lock (L) { return "{\"voice\":" + Q(voz) + ",\"culture\":" + Q(cultura) + ",\"words\":[" + string.Join(",", W) + "],\"visemes\":[" + string.Join(",", V) + "]}"; }
  }
}
"@
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voces = $s.GetInstalledVoices() | Where-Object { $_.Enabled }
$elegida = if ($Culture) { $voces | Where-Object { $_.VoiceInfo.Culture.Name -like "$Culture*" } | Select-Object -First 1 }
if (-not $elegida) { $elegida = $voces | Select-Object -First 1 }
if (-not $elegida) { throw "No hay ninguna voz local instalada" }
$s.SelectVoice($elegida.VoiceInfo.Name)
$s.Rate = $Rate
[Marcas]::Unir($s)
$formato = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(44100, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$s.SetOutputToWaveFile($Wav, $formato)
$texto = [IO.File]::ReadAllText($TextFile, [Text.Encoding]::UTF8)
$p = $s.SpeakAsync($texto)
while (-not $p.IsCompleted) { Start-Sleep -Milliseconds 40 }
Start-Sleep -Milliseconds 150
$s.SetOutputToNull()
$s.Dispose()
[IO.File]::WriteAllText($Json, [Marcas]::Json($elegida.VoiceInfo.Name, $elegida.VoiceInfo.Culture.Name), (New-Object Text.UTF8Encoding $false))
